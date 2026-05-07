# GitHub Copilot Agent Skills

This directory contains Agent Skills for GitHub Copilot - specialized capabilities that enable automated workflows and domain-specific tasks.

## What are Agent Skills?

Agent Skills are folders of instructions, scripts, and resources that GitHub Copilot can load when relevant to perform specialized tasks. Agent Skills follow an open standard (agentskills.io) that works across multiple AI agents, including:

- GitHub Copilot in VS Code
- GitHub Copilot CLI
- GitHub Copilot coding agent

Unlike custom instructions that primarily define coding guidelines, **Agent Skills enable specialized capabilities and workflows** that can include scripts, examples, and other resources.

### Key Benefits

- **Specialize Copilot:** Tailor capabilities for domain-specific tasks without repeating context
- **Reduce repetition:** Create once, use automatically across all conversations
- **Compose capabilities:** Combine multiple skills to build complex workflows
- **Efficient loading:** Only relevant content loads into context when needed
- **Portability:** Works across VS Code, Copilot CLI, and coding agent

### Agent Skills vs Custom Instructions

| Feature | Agent Skills | Custom Instructions |
|---------|--------------|---------------------|
| **Purpose** | Teach specialized capabilities and workflows | Define coding standards and guidelines |
| **Portability** | Works across VS Code, Copilot CLI, and coding agent | VS Code and GitHub.com only |
| **Content** | Instructions, scripts, examples, and resources | Instructions only |
| **Scope** | Task-specific, loaded on-demand | Always applied (or via glob patterns) |
| **Standard** | Open standard (agentskills.io) | VS Code-specific |

**Use Agent Skills when you want to:**
- Create reusable capabilities that work across different AI tools
- Include scripts, examples, or other resources alongside instructions
- Share capabilities with the wider AI community
- Define specialized workflows like testing, debugging, or deployment processes

**Use custom instructions when you want to:**
- Define project-specific coding standards
- Set language or framework conventions
- Specify code review or commit message guidelines
- Apply rules based on file types using glob patterns

## Available Skills

### [bin-name-override](bin-name-override/SKILL.md)

**Tool:** `bin_name_override.py`  
**Purpose:** Automatically detect and fix bin name mismatches between module `.sbdefs` files and the main `BinDefinitions.bdefs` file

**When to use:**
- Module `.sbdefs` parent bin names don't match `BinDefinitions.bdefs`
- After generating `.sbdefs` files from Pymtpl modules
- When adding new `setbin()` calls to a module
- Tests fail due to bin definition mismatches

**Key Features:**
- Compares `.sbdefs` against `.bdefs` to find parent bin name mismatches
- Generates properly formatted `bindefovrd` entries
- Smart merge: Updates only necessary entries while preserving existing customizations
- Suggests new bin definitions for missing parent bins

**Invoke with:**
```
/bin-name-override module.py module.sbdefs BinDefinitions.bdefs
```

**Related Instructions:** [BinDefinitions.instructions.md](../instructions/TOS/BinDefinitions.instructions.md)

---

### [module-creation](module-creation/SKILL.md)

**Tool:** `module-creation/create_module.py`  
**Purpose:** Automated workflow to create a new Pymtpl test module from scratch with all required files, directory structure, and solution references

**When to use:**
- Creating a new test module from scratch
- Scaffolding a module with proper configuration
- Setting up module structure with all required files
- Ensuring solution integration is correct

**Key Features:**
- Creates complete module directory structure with InputFiles folder
- Generates all configuration files (.mconfig, .BinLimits.json, .tpmodule, .mtproj)
- Populates Python source from template with product-specific Initialize class
- Updates solution files (.sln, .imp, .stpl, .tpproj)
- Compiles initial module and validates bin definitions

**Invoke with:**
```
/module-creation ModuleName --test-type <type>
```

**Related Instructions:** [13-module-creation.instructions.md](../instructions/pymtpl/13-module-creation.instructions.md)

---

### [pattern-patch-update](pattern-patch-update/SKILL.md)

**Tool:** `pattern_patch_update.py`  
**Purpose:** Bulk update pattern patch versions across multiple module `.mconfig` files

**When to use:**
- Updating pattern versions after pattern release
- Synchronizing pattern versions across module groups (e.g., all PTH modules)
- Bulk updating test pattern patches
- Reverting pattern versions across modules

**Key Features:**
- Finds all modules matching pattern (PTH*, CLK*, ARR*, etc.)
- Validates patch version format
- Updates Patch attribute in .mconfig XML files
- Preserves formatting and structure
- Reports all changes made

**Invoke with:**
```
/pattern_patch_update ModulePattern PatchVersion
```

**Related Instructions:** [mconfig.instructions.md](../instructions/mconfig.instructions.md)

---

### [module-optimization](module-optimization/SKILL.md)

**Tool:** `module_optimization.py`  
**Purpose:** Optimize Pymtpl module code by applying refactoring patterns (UserVars, templates, loops) with validation at each step

**When to use:**
- After converting .mtpl to .py format
- Reducing code duplication in modules
- Standardizing test instance parameters
- Improving module maintainability
- Refactoring legacy modules

**Key Features:**
- Analyzes module for optimization opportunities
- Creates detailed optimization plan
- Applies transformations incrementally (UserVars, templates, loops)
- Validates by compiling and comparing .mtpl output at each step
- Ensures functional equivalence throughout
- Documents changes with comments

**Invoke with:**
```
/module_optimization Module.py --dry-run
```

---

### [pymtpl-compiler](pymtpl-compiler/SKILL.md)

**Guide for:** Using `pymtpl.py` (Scripts/pytpd/main/pymtpl.py)  
**Purpose:** Instructions for compiling Pymtpl Python modules (.py) to generate test plan files (.mtpl, .sbdefs, .flw)

**When to use:**
- Compiling modules after editing .py files
- Regenerating .mtpl, .sbdefs, .flw files
- Validating module compilation before commit
- Running compilation in CI/CD pipelines
- Troubleshooting compilation errors

**Key Guidance:**
- Locating pymtpl.py in the repository
- Running from the correct directory (module directory)
- Using proper relative paths for Common.env and BinDefinitions.bdefs
- GitHub runner compatibility (-skip_path_updater flag)
- Validating generated output files

**Invoke with:**
```
/pymtpl_compiler ModuleName
```

**Related Instructions:** [01-module-workflow.instructions.md](../instructions/pymtpl/01-module-workflow.instructions.md)

---

### [test-instance-comparison](test-instance-comparison/SKILL.md)

**Tool:** `compare_test_instances.ps1` (wraps `ApiSamples.TestInstanceComparison.exe`)
**Purpose:** Extract and compare test instances and flows between one or two test programs using the Trace API. Walks `MainFlow.DeepSelect<TestInstance>()` so results reflect **true execution order**, not STPL/file/`.mtpl` listing order.

**When to use:**
- Comparing two test programs side-by-side (diff TPs)
- Listing test instances in a specific flow or module
- Determining the execution order of instances
- Checking what changed between two TP versions (presence, ordering, parameters, EDC, bypass)
- Analyzing flow-position changes for PatConfig / modification impact

**Key Features:**
- Three modes: `single`, `compare`, `mcp` (MCP server for AI integration)
- Handles STPL → TPL resolution automatically
- Case-insensitive substring matching on flow/module names
- CSV output with template, parent flow, parameters, MTT status

**Invoke with:**
```powershell
.\.github\skills\test-instance-comparison\compare_test_instances.ps1 `
    -StplPath <stpl> -TplPath <tpl> -ModuleName <pattern> -OutputCsvPath <csv>
```

**Related Instructions:** see "Comparing Test Instances and Flows Between Test Programs" in [copilot-instructions.md](../copilot-instructions.md).

---

## Creating a New Skill

**Tip:** Type `/skills` in the Copilot chat input to quickly open the Configure Skills menu.

### Quick Start

1. **Create a skill directory** in `.github/skills/` with a descriptive name (e.g., `webapp-testing`)
2. **Create a `SKILL.md` file** in the skill directory with proper YAML frontmatter
3. **Add scripts and resources** as needed (e.g., templates, examples)
4. **Link to the skill** from relevant instruction files
5. **Update this README** with a new entry

### SKILL.md File Format

Every skill must have a `SKILL.md` file with YAML frontmatter and detailed instructions:

```markdown
---
name: skill-name
description: Description of what the skill does and when to use it. Be specific about both capabilities and use cases to help Copilot decide when to load the skill.
argument-hint: [optional hint for slash command arguments]
user-invokable: true
disable-model-invocation: false
---

# Skill Name

Your detailed instructions, guidelines, and examples go here...

## What This Skill Does

Describe what the skill accomplishes...

## When to Use This Skill

Be specific about use cases...

## Usage

Provide clear examples...
```

### YAML Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | **Yes** | Unique identifier, lowercase with hyphens (e.g., `webapp-testing`). Max 64 chars. |
| `description` | **Yes** | What the skill does and when to use it. Be specific. Max 1024 chars. |
| `argument-hint` | No | Hint shown in chat input when invoked as slash command (e.g., `[test file] [options]`) |
| `user-invokable` | No | Whether skill appears as `/` slash command. Defaults to `true`. |
| `disable-model-invocation` | No | If `true`, requires manual invocation only (not auto-loaded). Defaults to `false`. |

### Skill Body Content

Include in your skill documentation:
- **What the skill helps accomplish**
- **When to use the skill** (be specific about use cases)
- **Step-by-step procedures to follow**
- **Examples of expected input and output**
- **References to included scripts or resources** using relative paths like `[script](./script.py)`

### Folder Structure

Each skill should have its own folder containing:

```
skill-name/
├── SKILL.md           # Skill definition (required)
├── script.py          # Automation script
├── template.js        # Template files
├── examples/          # Example files/scenarios
└── resources/         # Additional resources
```

**Example:**
```
bin-name-override/
├── SKILL.md               # Skill definition with YAML frontmatter
└── bin_name_override.py   # Python automation script
```

## Skill Locations

VS Code supports two types of skills:

| Skill Type | Location | Use Case |
|------------|----------|----------|
| **Project skills** | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | Repository-specific skills shared with team |
| **Personal skills** | `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | User-specific skills for personal use |

**Tip:** Configure additional locations using the `chat.agentSkillsLocations` setting in VS Code. This is useful for:
- Sharing skills across multiple projects
- Keeping skills in a centralized location
- Using skills from a shared team repository

## When to Use Skills vs Instructions

### Use Agent Skills when:
- The task is repetitive and automatable
- The solution requires parsing/analysis across multiple files
- Manual execution is error-prone
- A script or tool already exists or should be created
- You want the capability to work across different AI tools

### Use Custom Instructions when:
- Providing coding guidelines and best practices
- Documenting file format specifications
- Explaining conceptual patterns
- Guiding manual code review or editing
- Defining project-specific coding standards

## Resources

- [Agent Skills Standard](https://agentskills.io) - Official specification
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Custom Instructions](../instructions/README.md) - For coding guidelines and conventions
