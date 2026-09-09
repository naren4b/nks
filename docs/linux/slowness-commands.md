# Linux Response-Slowness Command Reference

Goal: quickly identify whether response delay originates in DNS, network/TLS, the application, CPU, memory, storage, resource limits, or the kernel.

**Related:** [Linux and Talos Operations](index.md) · [System setup](system-setup.md) · [Investigation guide](slowness-investigation.md)

> Replace placeholders before running. Some commands require `sudo`. Optional tools may come from `sysstat`, `dnsutils`/`bind-utils`, `iproute2`, `lsof`, `strace`, `netcat`, and `net-tools` packages.

## 1. Time and host load

```bash
date
uptime
```

## 2. Request timing

```bash
curl -sS -o /dev/null -w 'DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nFirst byte: %{time_starttransfer}s\nTotal: %{time_total}s\nHTTP: %{http_code}\n' '<URL>'
```

## 3. System overview

```bash
top
vmstat 1
```

## 4. CPU

```bash
nproc
mpstat -P ALL 1
pidstat -u 1
ps -eo pid,ppid,stat,comm,%cpu,%mem --sort=-%cpu | head -20
```

### Known process threads

```bash
top -H -p <PID>
ps -Lp <PID> -o pid,tid,psr,pcpu,stat,comm
```

## 5. Memory and swap

```bash
free -h
vmstat 1
cat /proc/meminfo
ps -eo pid,comm,%mem,rss,vsz --sort=-rss | head -20
swapon --show
```

### OOM events

```bash
sudo journalctl -k --since '1 hour ago' | grep -iE 'oom|out of memory|killed process'
sudo dmesg -T | grep -iE 'oom|out of memory|killed process'
```

## 6. Storage and filesystems

```bash
iostat -xz 1
pidstat -d 1
df -hT
df -i
sudo du -xhd1 /var 2>/dev/null | sort -h
```

### Open and deleted files

```bash
sudo lsof +L1
sudo lsof -p <PID>
```

## 7. Network

```bash
ip -s link
ss -s
ss -lntp
ss -antp
sar -n DEV 1
```

### TCP errors, drops, and retransmissions

```bash
netstat -s | grep -iE 'retrans|listen|drop|overflow'
nstat -az | grep -iE 'Retrans|Timeout|Listen|Drop'
```

### Dependency connectivity

```bash
ping -c 5 <HOST>
tracepath <HOST>
nc -vz -w 5 <HOST> <PORT>
curl -v --connect-timeout 5 '<URL>'
```

## 8. DNS

```bash
time getent hosts <HOST>
dig <HOST> +stats
resolvectl status
curl -v --resolve '<HOST>:443:<IP>' 'https://<HOST>/'
```

## 9. Blocked processes

```bash
ps -eo state,pid,ppid,wchan:30,comm,args | awk '$1 ~ /^D/'
ps -eo pid,stat,wchan:32,comm,args --sort=stat
```

### Trace a known process briefly

```bash
sudo strace -tt -T -p <PID>
```

## 10. File descriptors and limits

```bash
ulimit -a
cat /proc/<PID>/limits
find /proc/<PID>/fd -maxdepth 1 -type l 2>/dev/null | wc -l
cat /proc/sys/fs/file-nr
```

### Limit-related errors

```bash
sudo journalctl --since '30 minutes ago' | grep -iE 'too many open files|resource temporarily unavailable'
```

## 11. Service health and logs

```bash
systemctl status <SERVICE> --no-pager
sudo journalctl -u <SERVICE> --since '30 minutes ago' --no-pager
sudo journalctl -p warning --since '30 minutes ago' --no-pager
sudo journalctl -f -u <SERVICE>
systemctl show <SERVICE> -p ActiveEnterTimestamp -p ExecMainStartTimestamp -p NRestarts
```

## 12. Kernel and hardware events

```bash
sudo dmesg -T | tail -100
sudo journalctl -k --since '1 hour ago' --no-pager
sudo journalctl -k --since '1 hour ago' --no-pager | grep -iE 'error|timeout|reset|blocked|hung|I/O|segfault|thermal'
```

## Recommended order

```text
Measure request timing
→ Check CPU, run queue, memory, swap, and disk latency
→ Check network errors, connection states, and DNS
→ Identify the affected process
→ Inspect limits, service logs, and kernel events
→ Correlate findings by timestamp before remediation
```
