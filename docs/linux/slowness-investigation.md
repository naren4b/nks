# Linux Response-Slowness Investigation Guide

Use this guide when an application, API, SSH session, or Linux host is responding slowly. The goal is to locate the delay before changing configuration or restarting services.

**Related:** [Linux and Talos Operations](index.md) · [System setup](system-setup.md) · [Command reference](slowness-commands.md)

> Run read-only commands first. Replace `<URL>`, `<HOST>`, `<PORT>`, `<PID>`, and `<SERVICE>` with actual values. Some commands require `sudo`. Availability varies by distribution; `iostat`, `mpstat`, `pidstat`, and `sar` normally come from the `sysstat` package.

## Investigation flow

1. Measure where the request spends time.
2. Check system-wide CPU, memory, disk, and network pressure.
3. Identify the affected process or service.
4. Inspect logs, limits, and kernel events.
5. Correlate findings using timestamps before taking action.

## 1. Establish the time and host load

```bash
date
uptime
```

- `date` records the exact investigation time so metrics and logs can be correlated.
- `uptime` shows how long the host has been running, the number of logged-in users, and the 1-, 5-, and 15-minute load averages.
- Load average is not CPU percentage. Compare it with the number of logical CPUs from `nproc`. Persistent load greater than available CPUs suggests runnable or uninterruptible work is queuing.

## 2. Measure the request path

```bash
curl -sS -o /dev/null -w 'DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nFirst byte: %{time_starttransfer}s\nTotal: %{time_total}s\nHTTP: %{http_code}\n' '<URL>'
```

- `-sS` hides the progress meter but still displays errors.
- `-o /dev/null` discards the response body so the test focuses on timing.
- `time_namelookup` measures DNS resolution.
- `time_connect` measures elapsed time until the TCP connection is established.
- `time_appconnect` measures elapsed time through the TLS handshake.
- `time_starttransfer` measures time to the first response byte. A large gap after connection/TLS often points to server-side processing or an upstream dependency.
- `time_total` measures the full request duration.
- `http_code` confirms whether the request succeeded, failed, or was throttled.

Repeat the request several times. One slow sample can be caused by cold caches or a new connection.

## 3. Get a system-wide view

```bash
top
vmstat 1
```

- `top` shows processes, CPU use, memory use, load, and task states interactively. Press `1` to display individual CPU cores and `H` to show threads.
- `vmstat 1` prints one-second samples. Ignore the first row because it represents averages since boot.
- In `vmstat`, a high `r` value indicates runnable tasks waiting for CPU; a persistent `b` value indicates tasks blocked, commonly on I/O.
- High `wa` suggests I/O wait. Non-zero `si` or `so` indicates swap activity. High `us` means user-space CPU work; high `sy` means kernel work.

## 4. Investigate CPU pressure

```bash
nproc
mpstat -P ALL 1
pidstat -u 1
ps -eo pid,ppid,stat,comm,%cpu,%mem --sort=-%cpu | head -20
```

- `nproc` provides the logical CPU count used to interpret load and run queues.
- `mpstat -P ALL 1` reveals saturation or imbalance across CPU cores. High `%idle` means spare CPU; high `%iowait` points toward storage or remote filesystem delays.
- `pidstat -u 1` reports per-process CPU consumption every second and is easier to correlate over time than an interactive screen.
- `ps ... --sort=-%cpu` takes a snapshot of the top CPU-consuming processes. `stat` also exposes whether a process is running, sleeping, or blocked.

For a known process:

```bash
top -H -p <PID>
ps -Lp <PID> -o pid,tid,psr,pcpu,stat,comm
```

- `top -H -p` restricts the view to the process and displays its threads.
- `ps -L` maps thread IDs to CPU cores and CPU usage. One hot thread can saturate a single core while total host CPU appears acceptable.

## 5. Investigate memory and swapping

```bash
free -h
vmstat 1
cat /proc/meminfo
ps -eo pid,comm,%mem,rss,vsz --sort=-rss | head -20
swapon --show
```

- `free -h` summarizes RAM and swap. Focus on `available`, not just `free`, because Linux deliberately uses unused memory for cache.
- `vmstat 1` exposes active swapping through `si` and `so`. Persistent swap I/O can create severe response latency.
- `/proc/meminfo` provides detailed kernel memory counters when the summary is insufficient.
- `ps` ranks processes by resident memory (`rss`). `vsz` is virtual address space and does not equal physical consumption.
- `swapon --show` lists active swap devices or files.

Check whether the kernel killed a process because memory was exhausted:

```bash
sudo journalctl -k --since '1 hour ago' | grep -iE 'oom|out of memory|killed process'
sudo dmesg -T | grep -iE 'oom|out of memory|killed process'
```

- The first command searches recent kernel journal entries.
- The second searches the kernel ring buffer and is useful where persistent journaling is unavailable.
- OOM messages identify the killed process and confirm that memory pressure became critical.

## 6. Investigate storage and filesystem latency

```bash
iostat -xz 1
pidstat -d 1
df -hT
df -i
sudo du -xhd1 /var 2>/dev/null | sort -h
```

- `iostat -xz 1` reports extended per-device statistics every second. High `await` means requests are taking longer; sustained high `%util` and a growing queue suggest saturation. Interpret values against the storage type and normal baseline.
- `pidstat -d 1` identifies processes generating reads, writes, or I/O delay.
- `df -hT` detects full filesystems and shows filesystem types.
- `df -i` detects inode exhaustion, which can prevent new files even when byte capacity remains.
- `du -xhd1 /var` shows large directories without crossing into other mounted filesystems. It can be expensive on very large trees, so run it only when capacity is suspect.

Check for deleted files that remain open and continue consuming space:

```bash
sudo lsof +L1
sudo lsof -p <PID>
```

- `lsof +L1` finds open files whose link count is below one, often deleted log files retained by a running process.
- `lsof -p` lists files, sockets, and libraries held by one process.

## 7. Investigate network pressure

```bash
ip -s link
ss -s
ss -lntp
ss -antp
sar -n DEV 1
```

- `ip -s link` reports interface packet counts, errors, and drops. Increasing errors or drops indicate a host, driver, link, or capacity problem.
- `ss -s` gives a concise socket summary.
- `ss -lntp` confirms which TCP ports are listening and which process owns them.
- `ss -antp` shows TCP connection states and process ownership. Large or growing counts in `SYN-RECV`, `CLOSE-WAIT`, or `TIME-WAIT` require context and trend comparison.
- `sar -n DEV 1` shows interface throughput and packet rates every second.

Inspect TCP failures and retransmissions:

```bash
netstat -s | grep -iE 'retrans|listen|drop|overflow'
nstat -az | grep -iE 'Retrans|Timeout|Listen|Drop'
```

- `netstat -s` summarizes protocol counters. It may require the legacy `net-tools` package.
- `nstat -az` provides kernel network counters and is the modern alternative on many systems.
- Increasing retransmission, timeout, listen-drop, or overflow counters supports a network-loss or server-backlog hypothesis. A static historical counter alone does not prove a current incident.

Test the path to a dependency:

```bash
ping -c 5 <HOST>
tracepath <HOST>
nc -vz -w 5 <HOST> <PORT>
curl -v --connect-timeout 5 '<URL>'
```

- `ping` checks ICMP reachability and round-trip variation, but firewalls may block it even when the service works.
- `tracepath` helps reveal routing or path-MTU issues without proving application health.
- `nc` verifies that a TCP connection to the target port can be established.
- Verbose `curl` exposes name resolution, address selection, connection, TLS, and HTTP details.

## 8. Isolate DNS delays

```bash
time getent hosts <HOST>
dig <HOST> +stats
resolvectl status
curl -v --resolve '<HOST>:443:<IP>' 'https://<HOST>/'
```

- `getent hosts` tests name resolution through the host's configured Name Service Switch, which is closer to application behavior than querying DNS alone.
- `dig +stats` reports DNS server response time and the resolver used.
- `resolvectl status` shows resolver configuration on systems using `systemd-resolved`.
- `curl --resolve` bypasses normal DNS for this request while preserving the hostname for TLS and HTTP. If this is consistently fast while normal requests are slow, DNS becomes a strong suspect.

## 9. Find blocked or abnormal processes

```bash
ps -eo state,pid,ppid,wchan:30,comm,args | awk '$1 ~ /^D/'
ps -eo pid,stat,wchan:32,comm,args --sort=stat
```

- The first command shows tasks in `D` state: uninterruptible sleep, frequently caused by local disk, NFS, or kernel I/O waits.
- The second lists every process with its state and kernel wait channel.
- Common states are `R` (running/runnable), `S` (interruptible sleep), `D` (uninterruptible sleep), `T` (stopped), and `Z` (zombie).

Trace a known process briefly:

```bash
sudo strace -tt -T -p <PID>
```

- `-tt` adds precise timestamps and `-T` reports time spent in each system call.
- Long `connect()` calls suggest network or dependency issues; long `read()` or `write()` calls may indicate storage or network delay; repeated `futex()` activity can indicate lock contention.
- Tracing adds overhead. Use it briefly, preferably outside peak load, and stop with `Ctrl+C`.

## 10. Check file descriptors and process limits

```bash
ulimit -a
cat /proc/<PID>/limits
find /proc/<PID>/fd -maxdepth 1 -type l 2>/dev/null | wc -l
cat /proc/sys/fs/file-nr
```

- `ulimit -a` shows limits inherited by the current shell; these may differ from a service's limits.
- `/proc/<PID>/limits` shows the effective limits of the affected process.
- Counting `/proc/<PID>/fd` shows how many file descriptors that process currently has open.
- `/proc/sys/fs/file-nr` shows system-wide allocated, unused, and maximum file-handle values.

Search for resource-limit errors:

```bash
sudo journalctl --since '30 minutes ago' | grep -iE 'too many open files|resource temporarily unavailable'
```

- These messages indicate file-descriptor, process/thread, or another resource limit may be rejecting work.

## 11. Inspect the service and its logs

```bash
systemctl status <SERVICE> --no-pager
sudo journalctl -u <SERVICE> --since '30 minutes ago' --no-pager
sudo journalctl -p warning --since '30 minutes ago' --no-pager
sudo journalctl -f -u <SERVICE>
systemctl show <SERVICE> -p ActiveEnterTimestamp -p ExecMainStartTimestamp -p NRestarts
```

- `systemctl status` shows whether the service is active, failed, or restarting, plus recent log lines.
- The first `journalctl` command restricts logs to the affected service and incident window.
- The second finds warnings and higher-priority system events during that window.
- `journalctl -f` follows new service logs while a slow request is reproduced. Stop with `Ctrl+C`.
- `systemctl show` reveals service start times and restart count, helping detect crash loops or recent restarts.

## 12. Check kernel and hardware signals

```bash
sudo dmesg -T | tail -100
sudo journalctl -k --since '1 hour ago' --no-pager
sudo journalctl -k --since '1 hour ago' --no-pager | grep -iE 'error|timeout|reset|blocked|hung|I/O|segfault|thermal'
```

- Recent kernel output can reveal disk resets, network-driver failures, hung tasks, filesystem errors, thermal throttling, and application crashes.
- Do not act on a matching word alone. Confirm its timestamp, device, repetition, and relationship to the slowdown.

## Evidence to capture before remediation

Record the slow URL or operation, exact UTC/local timestamp, affected host and service, request timings, load average, CPU/run queue, available memory and swap activity, disk `await`, network drops/retransmissions, process PID/state, and relevant logs.

Avoid restarting the service before collecting evidence unless availability demands it. A restart may restore service while removing the clearest evidence of the root cause.

