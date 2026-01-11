<!-- AUTO-GENERATED - DO NOT EDIT -->
<!-- Run: ./scripts/generate_cli_docs.py -->
<!-- dprint-ignore-file -->
<!-- markdownlint-disable-file -->

# CLI Reference

Documentation for the `procclean` script.

```console
procclean --help
```

<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight"><span style="color: #98f641; text-decoration-color: #98f641">Usage:</span> <span style="color: #98f641; text-decoration-color: #98f641">procclean</span> [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-h</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-v</span>] <span style="color: #54ebdd; text-decoration-color: #54ebdd">{list,ls,groups,g,kill,memory,mem}</span> <span style="color: #54ebdd; text-decoration-color: #54ebdd">...</span>

<span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Process cleanup tool with TUI and CLI interfaces.</span>

<span style="color: #98f641; text-decoration-color: #98f641">Positional Arguments:</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">{list,ls,groups,g,kill,memory,mem}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Commands</span>
    <span style="color: #54ebdd; text-decoration-color: #54ebdd">list (ls)</span>           <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">List processes</span>
    <span style="color: #54ebdd; text-decoration-color: #54ebdd">groups (g)</span>          <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Show process groups</span>
    <span style="color: #54ebdd; text-decoration-color: #54ebdd">kill</span>                <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Kill process(es)</span>
    <span style="color: #54ebdd; text-decoration-color: #54ebdd">memory (mem)</span>        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Show memory summary</span>

<span style="color: #98f641; text-decoration-color: #98f641">Options:</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-h</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--help</span>            <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show this help message and exit</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-v</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--version</span>         <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show program&#x27;s version number and exit</span>
</code>
</pre>

## `list` / `ls`

```console
procclean list --help
```

<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight"><span style="color: #98f641; text-decoration-color: #98f641">Usage:</span> <span style="color: #98f641; text-decoration-color: #98f641">procclean list</span> [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-h</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-f</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{table,json,csv,md}</span>]
                      [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-s</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{memory,mem,cpu,pid,name,cwd}</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-a</span>]
                      [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-F</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{killable,orphans,high-memory}</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-k</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-o</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-m</span>]
                      [<span style="color: #54ebdd; text-decoration-color: #54ebdd">--high-memory-threshold</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">MB</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">--min-memory</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">MB</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-n</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">N</span>]
                      [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-c</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">COLS</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">--cwd</span> [<span style="color: #7af0e5; text-decoration-color: #7af0e5">PATH</span>]]

<span style="color: #98f641; text-decoration-color: #98f641">Options:</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-h</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--help</span>            <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show this help message and exit</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-f</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--format</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{table,json,csv,md}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Output format (default: table)</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-s</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--sort</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{memory,mem,cpu,pid,name,cwd}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Sort by field (default: memory)</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-a</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--ascending</span>       <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Sort ascending instead of descending</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-F</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--filter</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{killable,orphans,high-memory}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Filter preset: killable (orphans, not tmux, not</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">system), orphans, high-memory</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-k</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--killable</span>        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #54ebdd; text-decoration-color: #54ebdd">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> killable</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-o</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--orphans</span>         <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #54ebdd; text-decoration-color: #54ebdd">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> orphans</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-m</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--high-memory</span>     <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #54ebdd; text-decoration-color: #54ebdd">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> high-memory</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">--high-memory-threshold</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">MB</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Threshold for high memory filter (default: 500 MB)</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">--min-memory</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">MB</span>       <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Minimum memory to include (default: 5 MB)</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-n</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--limit</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">N</span>         <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Limit output to N processes</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-c</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--columns</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">COLS</span>    <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Comma-separated columns</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">(pid,name,rss_mb,cpu_percent,cwd,ppid,parent_name,stat</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">us,cmdline,username)</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">--cwd</span> [<span style="color: #7af0e5; text-decoration-color: #7af0e5">PATH</span>]          <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Filter by cwd (no value = current dir, or specify</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">path/glob)</span>
</code>
</pre>

## `groups` / `g`

```console
procclean groups --help
```

<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight"><span style="color: #98f641; text-decoration-color: #98f641">Usage:</span> <span style="color: #98f641; text-decoration-color: #98f641">procclean groups</span> [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-h</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-f</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{table,json}</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">--min-memory</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">MB</span>]

<span style="color: #98f641; text-decoration-color: #98f641">Options:</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-h</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--help</span>            <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show this help message and exit</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-f</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--format</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{table,json}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Output format (default: table)</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">--min-memory</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">MB</span>       <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Minimum memory to include (default: 5 MB)</span>
</code>
</pre>

## `kill`

```console
procclean kill --help
```

<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight"><span style="color: #98f641; text-decoration-color: #98f641">Usage:</span> <span style="color: #98f641; text-decoration-color: #98f641">procclean kill</span> [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-h</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-f</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-y</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">--cwd</span> [<span style="color: #7af0e5; text-decoration-color: #7af0e5">PATH</span>]]
                      [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-F</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{killable,orphans,high-memory}</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-k</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-o</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-m</span>]
                      [<span style="color: #54ebdd; text-decoration-color: #54ebdd">--min-memory</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">MB</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">--high-memory-threshold</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">MB</span>]
                      [<span style="color: #54ebdd; text-decoration-color: #54ebdd">--preview</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-O</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{table,json,csv,md}</span>]
                      [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-s</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{memory,mem,cpu,pid,name,cwd}</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-n</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">N</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-c</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">COLS</span>]
                      [<span style="color: #54ebdd; text-decoration-color: #54ebdd">PID</span> <span style="color: #54ebdd; text-decoration-color: #54ebdd">...</span>]

<span style="color: #98f641; text-decoration-color: #98f641">Positional Arguments:</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">PID</span>                   <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Process ID(s) to kill (or use filters)</span>

<span style="color: #98f641; text-decoration-color: #98f641">Options:</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-h</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--help</span>            <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show this help message and exit</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-f</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--force</span>           <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Force kill (SIGKILL instead of SIGTERM)</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-y</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--yes</span>             <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Skip confirmation prompt</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">--cwd</span> [<span style="color: #7af0e5; text-decoration-color: #7af0e5">PATH</span>]          <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Kill processes in cwd (no value = current dir, or</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">specify path/glob)</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-F</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--filter</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{killable,orphans,high-memory}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Filter preset to select processes</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-k</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--killable</span>        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #54ebdd; text-decoration-color: #54ebdd">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> killable</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-o</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--orphans</span>         <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #54ebdd; text-decoration-color: #54ebdd">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> orphans</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-m</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--high-memory</span>     <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #54ebdd; text-decoration-color: #54ebdd">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> high-memory</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">--min-memory</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">MB</span>       <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Minimum memory for filter (default: 5 MB)</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">--high-memory-threshold</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">MB</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Threshold for high memory filter (default: 500 MB)</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">--preview</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--dry-run</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--dry</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Show what would be killed without killing</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-O</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--out-format</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{table,json,csv,md}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Output format for preview (default: table)</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-s</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--sort</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{memory,mem,cpu,pid,name,cwd}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Sort by field for preview</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-n</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--limit</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">N</span>         <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Limit preview output to N processes</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-c</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--columns</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">COLS</span>    <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Comma-separated columns for preview</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">(pid,name,rss_mb,cpu_percent,cwd,ppid,parent_name,stat</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">us,cmdline,username)</span>
</code>
</pre>

## `memory` / `mem`

```console
procclean memory --help
```

<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight"><span style="color: #98f641; text-decoration-color: #98f641">Usage:</span> <span style="color: #98f641; text-decoration-color: #98f641">procclean memory</span> [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-h</span>] [<span style="color: #54ebdd; text-decoration-color: #54ebdd">-f</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{table,json}</span>]

<span style="color: #98f641; text-decoration-color: #98f641">Options:</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-h</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--help</span>            <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show this help message and exit</span>
  <span style="color: #54ebdd; text-decoration-color: #54ebdd">-f</span>, <span style="color: #54ebdd; text-decoration-color: #54ebdd">--format</span> <span style="color: #7af0e5; text-decoration-color: #7af0e5">{table,json}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Output format (default: table)</span>
</code>
</pre>
