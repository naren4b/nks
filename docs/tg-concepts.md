# Terragrunt Essentials: Scaling DRY Infrastructure
![tf-tg-gl-tg-setup](https://github.com/user-attachments/assets/c0969d92-4f61-4244-a48f-404ef8343abe)

To establish a streamlined workflow for managing multi-environment infrastructure by leveraging Terragrunt to keep Terraform code "DRY" (Don't Repeat Yourself), manage remote state automatically, and orchestrate dependent modules.

**The Core Problem: Terraform at Scale**
- **Code Duplication:** Standard Terraform often leads to copying/pasting backend configurations and provider blocks across multiple environments (Dev, QA, Prod).
- **State Management:** Manually configuring S3 buckets/DynamoDB tables for every module is error-prone.
  
**Terragrunt Solutions**
- **DRY Backends**: Define the remote state configuration once in a root terragrunt.hcl file. Child modules inherit this, automatically creating the necessary S3 buckets/folders.
- **DRY Input Variables**: Use inputs blocks to pass variables to Terraform modules without redefining them in every environment.
- **Module Orchestration**: Use the dependency block to pass outputs from one module (e.g., a VPC) as inputs to another (e.g., an EKS cluster), ensuring they are applied in the correct order.
- **Hook & Execute:** Run custom commands before or after Terraform execution (e.g., cleaning up cache or running security scans) using `before_hook` and `after_hook`.

**^Pro-Tip:** The Folder Structure
Organize by Account > Region > Environment > Component. This hierarchy allows Terragrunt to use find_in_parent_folders() to dynamically pull configurations based on where the command is executed.

## Concepts of Terragrunt 

##  1. Terragrunt
Terragrunt is a flexible orchestration tool that allows Infrastructure as Code written in OpenTofu/Terraform to scale.
It differs from many other IaC tools in that it is designed to be an orchestrator for OpenTofu/Terraform execution, rather than primarily provisioning infrastructure itself. 

## 2. OpenTofu
OpenTofu is an open-source Infrastructure as Code tool spawned as a fork of Terraform after the license change from the Mozilla Public License (MPL) to the Business Source License (BSL).

OpenTofu was created as a drop-in replacement for Terraform (as it was forked from the same MPL source code), and is designed to be fully compatible with Terraform configurations and modules.

## 3. Unit
A unit is a single instance of infrastructure managed by Terragrunt. It has its own state, and can be detected by the presence of a terragrunt.hcl file in a directory.

Units typically represent a minimal useful piece of infrastructure that should be independently managed.

e.g. A unit might represent a single VPC, a single database, or a single server.

Units are designed to be contained, and can be operated on independently of other units. Infrastructure changes to units are also meant to be atomic. The interface you have with a unit is a single terragrunt.hcl file, and any change you make to it should result in one reproducible change to a limited subset of your infrastructure.


When Terragrunt finds the terraform block with a source parameter in live/stage/app/terragrunt.hcl file, it will:

1. Download the configurations specified via the source
2. Copy all files from the current working directory into the temporary folder.
3. Execute whatever OpenTofu/Terraform command you specified in that temporary folder.
4. Set any variables defined in the inputs = { …​ } block as environment variables (prefixed with TF_VAR_) before running your OpenTofu/Terraform code. 

ref: [terragrunt-infrastructure-modules-example](https://github.com/gruntwork-io/terragrunt-infrastructure-modules-example)

Working with lock files


## 4. Stack
A stack is a collection of units managed by Terragrunt. There is (as of writing) work underway to provide a top level artifact for interacting with stacks via a terragrunt.stack.hcl file, but as of now, stacks are generally defined by a directory with a tree of units. Units within a stack can be dependent on each other, and can be updated in a specific order to ensure that dependencies are resolved in the correct order.

Stacks typically represent a collection of units that need to be managed in concert.

e.g. A stack might represent a collection of units that together form a single application environment, a business unit, or a region.

A stack in Terragrunt is a collection of related units that can be managed together. Stacks provide a way to:

- Deploy multiple infrastructure components with a single command
- Manage dependencies between units automatically
- Control the blast radius of changes
- Organize infrastructure into logical groups
- Terragrunt supports two approaches to defining stacks:

    - Implicit Stacks: Created by organizing units in a directory structure.
    - Explicit Stacks: Defined using terragrunt.stack.hcl files.

### Implicit Stacks
The simplest way to create a stack is to organize your units in a directory structure in your repository. When you have multiple units in a directory, Terragrunt automatically treats that directory as a stack 

**Advantages of Implicit Stacks**

- Simple: Just organize units in directory trees.
- Familiar: Organized following best practices for OpenTofu/Terraform repository structures.
- Flexible: Easy to add/remove units by creating/deleting directories.
- Version Control Friendly: Each unit is a separate directory with its own history.
- Backwards Compatible: This has been the default way to work with Terragrunt for over eight years, and the majority of existing - Terragrunt configurations use this approach.

**Limitations of Implicit Stacks**
- Manual Management: Each unit must be manually created and configured.
- No Reusability: Patterns can’t be easily shared across environments.
- Repetitive: Similar configurations must be duplicated or referenced from includes.

### Explicit Stacks
For an alternate approach (that is more flexible, but not necessarily always the better solution), you can define explicit stacks using terragrunt.stack.hcl files. These are blueprints that programmatically generate units at runtime.

**What is a terragrunt.stack.hcl file?**
A terragrunt.stack.hcl file is a blueprint that defines how to generate Terragrunt configurations programmatically. It tells Terragrunt:
    - What units to create.
    - Where to get their configurations from.
    - Where to place them in the directory structure.
    - What values to pass to each unit.

**Supported Configuration Blocks**
- unit blocks - Define Individual Infrastructure Components
    Purpose: Define a single, deployable piece of infrastructure.
    Use case: When you want to create a single piece of isolated infrastructure (e.g. a specific VPC, database, or application).
    Result: Generates a directory with a single terragrunt.hcl file in the specified path from the specified source.
- stack blocks - Define Reusable Infrastructure Patterns
    Purpose: Define a stack of units to be deployed together.
    Use case: When you have a common, multi-unit pattern (like “dev environment” or “three-tier web application”) that you want to deploy multiple times.
    Result: Generates a directory with another terragrunt.stack.hcl file in the specified path from the specified source.
    Two patterns 
    - Simple Stack with Units 
    - Nested Stack with Reusable Patterns
     - Advantages of Explicit Stacks
        Reusability: Define patterns once, reuse them across environments.
        Consistency: Ensure all environments follow the same structure.
        Version Control: Version collections of infrastructure patterns alongside the units of infrastructure that make them up.
        Automation: Generate complex infrastructure from simple blueprints.
        Flexibility: Easy to create variations with different values.
    - Limitations of Explicit Stacks
        Complexity: Requires understanding another configuration file.
        Generation Overhead: Units must be generated before use.
        Debugging: Generated files can be harder to debug if you accidentally generate files that are not what you intended.

**Choosing Between Implicit and Explicit Stacks**
    Use Implicit Stacks When:
    - You have a small number of units.
    - Each unit is unique and not repeated across environments.
    - You don’t mind a high file count.
    - You’re just getting started with Terragrunt.
    - You need maximum explicitness and transparency.
    Use Explicit Stacks When:
    - You have multiple environments (dev, staging, prod).
    - You want to reuse collections of related infrastructure patterns.
    - You have many similar units that differ only in values.
    - You want to version collections of infrastructure patterns.
    - You’re building infrastructure catalogs or templates.
** The Complete Workflow **
    For Implicit Stacks:
    - Organize: Create directories for each unit with terragrunt.hcl files.
    - Configure: Set up inputs, dependencies, etc. in each unit.
    - Deploy: Use terragrunt run --all apply to deploy all units.
    For Explicit Stacks:
    - Catalog: Create a catalog of infrastructure patterns (using terragrunt.hcl files, terragrunt.stack.hcl files, etc.) in a Git repository.
    - Author: Write a terragrunt.stack.hcl file with unit and/or stack blocks.
    - Generate: Run terragrunt stack generate to create the actual units*.
    - Deploy: Run terragrunt stack run apply to deploy all units**.

**Known Limitations of Explicit Stacks**
- Dependencies cannot be set on stacks ( it's written in individual unit's terragrunt.hcl _with 'dependency' block_ )
- Deeply nested stack generation can be slow
- Includes are not supported in terragrunt.stack.hcl files ( it's written in individual unit's terragrunt.hcl _with 'include' block_ )


## 5. Module
A module is an OpenTofu/Terraform construct defined using a collection of OpenTofu/Terraform configurations ending in .tf (or .tofu in the case of OpenTofu) that represent a general pattern of infrastructure that can be instantiated multiple times.

Modules typically represent a generic pattern of infrastructure that can be instantiated multiple times, with different configurations exposed as variables.

e.g. A module might represent a generic pattern for a VPC, a database, or a server. Note that this differs from a unit, which represents a single instance of a provisioned VPC, database, or server.

Modules can be located either in the local filesystem, in a remote repository, or in any of [these supported locations](https://opentofu.org/docs/language/modules/sources/).

To integrate a module into a Terragrunt unit, reference the module using the source attribute of the terraform block.
Just as importantly, since the OpenTofu/Terraform module code is now defined in a single repo, you can version it (e.g., using Git tags and referencing them using the ref parameter in the source URL, as in the stage/app/terragrunt.hcl and prod/app/terragrunt.hcl examples above), and promote a single, immutable version through each environment (e.g., qa → stage → prod).

A common pattern in Terragrunt usage is to only ever provision versioned, immutable modules. This is because Terragrunt is designed to be able to manage infrastructure over long periods of time, and it is important to be able to reproduce the state of infrastructure at any point in time.


## 6. Resource
A resource is a low level building block of infrastructure that is defined in OpenTofu/Terraform configurations.

Resources are typically defined in modules, but don’t have to be. Terragrunt can provision resources defined with .tf files that are not part of a module, located adjacent to the terragrunt.hcl file of a unit.

e.g. A resource might represent a single S3 bucket, or a single load balancer.

Resources generally correspond to the smallest piece of infrastructure that can be managed by OpenTofu/Terraform, and each resource has a specific address in state.
## 7. State
Terragrunt stores the current state of infrastructure in one or more OpenTofu/Terraform state files.

State is an extremely important concept in the context of OpenTofu/Terraform, and it’s helpful to read the relevant documentation there to understand what Terragrunt does to it.

Terragrunt has myriad capabilities that are designed to make working with state easier, including tooling to bootstrap state backend resources on demand, managing unit interaction with external state, and segmenting state.

The most common way in which state is segmented in Terragrunt projects is to take advantage of filesystem directory structures. Most Terragrunt projects are configured to store state in remote backends like S3 with keys that correspond to the relative path to the unit directory within a project, relative to the root terragrunt.hcl file. 
## 8. Directed Acyclic Graph (DAG)
The way in which units are resolved within a stack is via a Directed Acyclic Graph (DAG).

This graph is also used to determine the order in which resources are resolved within a unit. Dependencies in a DAG determine the order in which resources are created, updated, or destroyed.

## 9. Don’t Repeat Yourself (DRY)
The Don’t Repeat Yourself (DRY) principle is a software development principle that states that duplication in code should be avoided.

## 10. Blast Radius
Blast Radius is a term used in software development to describe the potential impact of a change, derived from the term used to describe the potential impact of an explosion.

In the context of infrastructure management, blast radius is used to describe the potential impact (negative or positive) of a change to infrastructure. The larger the blast radius, the more potential impact a change has.

## 11. Dependency
A dependency is a relationship between two units in a stack that results in data being passed from the dependency to the dependent unit.

Dependencies are defined in Terragrunt configuration files using the dependency block.

## 12. Include
The term “include” is used in two different contexts in Terragrunt.

- Include in configuration: This is when one configuration file is included as partial configuration in another configuration file. This is done using the include block in Terragrunt configuration files.
- Include in the Run Queue: This is when a unit is included in the Run Queue. There are multiple ways for a unit to be included in the Run Queue.
## 13. Exclude
The term “exclude” is only used in the context of excluding units from the Run Queue.


## 14. Feature
A feature is a configuration that can be dynamically controlled in Terragrunt configurations.

## 15. IaC Engine
IaC Engines (typically abbreviated “Engines”) are a way to extend the capabilities of Terragrunt by allowing users to control exactly how Terragrunt performs runs.

## 16. Infrastructure Estate
An infrastructure estate is all the infrastructure that a person or organization manages. This can be as small as a single resource, or as large as a collection of repositories containing one or more stacks.

Generally speaking, the larger the infrastructure estate, the more important it is to have good tooling for managing it. Terragrunt is designed to be able to manage infrastructure estates of any size, and is used by organizations of all sizes to manage their infrastructure efficiently.

## 17. Lock File Handling
An OpenTofu configuration may refer to two different kinds of external dependency that come from outside of its own codebase:

Providers, which are plugins for OpenTofu that extend it with support for interacting with various external systems.
Modules, which allow splitting out groups of OpenTofu configuration constructs (written in the OpenTofu language) into reusable abstractions.
Both of these dependency types can be published and updated independently from OpenTofu itself and from the configurations that depend on them. For that reason, OpenTofu must determine which versions of those dependencies are potentially compatible with the current configuration and which versions are currently selected for use.

Terraform 0.14 introduced lock files. These should mostly “just work” with Terragrunt version v0.27.0 and above: that is, the lock file (.terraform.lock.hcl) will be generated next to your terragrunt.hcl, and you should check it into version control.

1. Run Terragrunt as usual (e.g., run terragrunt plan, terragrunt apply, etc.).
2. Check the .terraform.lock.hcl file into version control.

## 18. Terragrunt caching
The first time you set the source parameter to a remote URL, Terragrunt will download the code from that URL into a tmp folder. It will NOT download it again afterwards unless you change that URL. That’s because downloading code—and more importantly, reinitializing remote state, redownloading provider plugins, and redownloading modules—can take a long time. To avoid adding 10-90 seconds of overhead to every Terragrunt command, Terragrunt assumes all remote URLs are immutable, and only downloads them once.

Working locally
```bash
cd live/stage/app
terragrunt apply --source ../../../modules//app
# If you need to force Terragrunt to redownload something from a remote URL, run Terragrunt with the --source-update
```

## 19. Working with relative file paths
One of the gotchas with downloading OpenTofu/Terraform configurations is that when you run terragrunt apply in folder foo, OpenTofu/Terraform will actually run in some temporary folder such as .terragrunt-cache/foo. That means you have to be especially careful with relative file paths, as they will be relative to that temporary folder and not the folder where you ran Terragrunt!

- Command line: When using file paths on the command line, such as passing an extra -var-file argument, you should use absolute paths:

```
# Use absolute file paths on the CLI!
terragrunt apply -var-file /foo/bar/extra.tfvars
```
- Terragrunt configuration: When using file paths directly in your Terragrunt configuration (terragrunt.hcl), such as in an extra_arguments block, you can’t use hard-coded absolute file paths, or it won’t work on your teammates’ computers. 
```hcl
terraform {
  source = "git::git@github.com:foo/modules.git//frontend-app?ref=v0.0.3"
  extra_arguments "custom_vars" {
    commands = [
      "apply",
      "plan",
      "import",
      "push",
      "refresh"
    ]
    # With the get_terragrunt_dir() function, you can use relative paths!
    arguments = [
      "-var-file=${get_terragrunt_dir()}/../common.tfvars",
      "-var-file=example.tfvars"
    ]
  }
}
```
## 20. Using Terragrunt with private Git repos
The easiest way to use Terragrunt with private Git repos is to use SSH authentication. Configure your Git account so you can use it with SSH (see the guide for GitHub here) and use the SSH URL for your repo:
```hcl
terragrunt.hcl
terraform {
  source = "git@github.com:foo/modules.git//path/to/module?ref=v0.0.1"
}
```
Look up the Git repo for your repository to find the proper format. Note: In automated pipelines, you may need to run the following command for your Git repository prior to calling terragrunt to ensure that the ssh host is registered locally, e.g.:

```
ssh -T -oStrictHostKeyChecking=accept-new git@github.com || true
```
