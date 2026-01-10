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
<code style="font-family:inherit" class="nohighlight"><span style="color: #00ff00; text-decoration-color: #00ff00">Usage:</span> <span style="color: #00ff00; text-decoration-color: #00ff00">procclean</span> [<span style="color: #00ffff; text-decoration-color: #00ffff">-h</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-v</span>] <span style="color: #00ffff; text-decoration-color: #00ffff">{list,ls,groups,g,kill,memory,mem}</span> <span style="color: #00ffff; text-decoration-color: #00ffff">...</span>

<span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Process cleanup tool with TUI and CLI interfaces.</span>

<span style="color: #00ff00; text-decoration-color: #00ff00">Positional Arguments:</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">{list,ls,groups,g,kill,memory,mem}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Commands</span>
    <span style="color: #00ffff; text-decoration-color: #00ffff">list (ls)</span>           <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">List processes</span>
    <span style="color: #00ffff; text-decoration-color: #00ffff">groups (g)</span>          <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Show process groups</span>
    <span style="color: #00ffff; text-decoration-color: #00ffff">kill</span>                <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Kill process(es)</span>
    <span style="color: #00ffff; text-decoration-color: #00ffff">memory (mem)</span>        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Show memory summary</span>

<span style="color: #00ff00; text-decoration-color: #00ff00">Options:</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-h</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--help</span>            <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show this help message and exit</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-v</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--version</span>         <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show program&#x27;s version number and exit</span>
</code>
</pre>

## `list` / `ls`

```console
procclean list --help
```

<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight"><span style="color: #00ff00; text-decoration-color: #00ff00">Usage:</span> <span style="color: #00ff00; text-decoration-color: #00ff00">procclean list</span> [<span style="color: #00ffff; text-decoration-color: #00ffff">-h</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-f</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{table,json,csv,md}</span>]
                      [<span style="color: #00ffff; text-decoration-color: #00ffff">-s</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{memory,mem,cpu,pid,name,cwd}</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-a</span>]
                      [<span style="color: #00ffff; text-decoration-color: #00ffff">-F</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{killable,orphans,high-memory}</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-k</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-o</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-m</span>]
                      [<span style="color: #00ffff; text-decoration-color: #00ffff">--high-memory-threshold</span> <span style="color: #00ffff; text-decoration-color: #00ffff">MB</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">--min-memory</span> <span style="color: #00ffff; text-decoration-color: #00ffff">MB</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-n</span> <span style="color: #00ffff; text-decoration-color: #00ffff">N</span>]
                      [<span style="color: #00ffff; text-decoration-color: #00ffff">-c</span> <span style="color: #00ffff; text-decoration-color: #00ffff">COLS</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">--cwd</span> [<span style="color: #00ffff; text-decoration-color: #00ffff">PATH</span>]]

<span style="color: #00ff00; text-decoration-color: #00ff00">Options:</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-h</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--help</span>            <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show this help message and exit</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-f</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--format</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{table,json,csv,md}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Output format (default: table)</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-s</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--sort</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{memory,mem,cpu,pid,name,cwd}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Sort by field (default: memory)</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-a</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--ascending</span>       <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Sort ascending instead of descending</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-F</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--filter</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{killable,orphans,high-memory}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Filter preset: killable (orphans, not tmux, not</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">system), orphans, high-memory</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-k</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--killable</span>        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #00ffff; text-decoration-color: #00ffff">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> killable</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-o</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--orphans</span>         <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #00ffff; text-decoration-color: #00ffff">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> orphans</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-m</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--high-memory</span>     <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #00ffff; text-decoration-color: #00ffff">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> high-memory</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">--high-memory-threshold</span> <span style="color: #00ffff; text-decoration-color: #00ffff">MB</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Threshold for high memory filter (default: 500 MB)</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">--min-memory</span> <span style="color: #00ffff; text-decoration-color: #00ffff">MB</span>       <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Minimum memory to include (default: 5 MB)</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-n</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--limit</span> <span style="color: #00ffff; text-decoration-color: #00ffff">N</span>         <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Limit output to N processes</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-c</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--columns</span> <span style="color: #00ffff; text-decoration-color: #00ffff">COLS</span>    <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Comma-separated columns</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">(pid,name,rss_mb,cpu_percent,cwd,ppid,parent_name,stat</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">us,cmdline,username)</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">--cwd</span> [<span style="color: #00ffff; text-decoration-color: #00ffff">PATH</span>]          <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Filter by cwd (no value = current dir, or specify</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">path/glob)</span>
</code>
</pre>

## `groups` / `g`

```console
procclean groups --help
```

<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight"><span style="color: #00ff00; text-decoration-color: #00ff00">Usage:</span> <span style="color: #00ff00; text-decoration-color: #00ff00">procclean groups</span> [<span style="color: #00ffff; text-decoration-color: #00ffff">-h</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-f</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{table,json}</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">--min-memory</span> <span style="color: #00ffff; text-decoration-color: #00ffff">MB</span>]

<span style="color: #00ff00; text-decoration-color: #00ff00">Options:</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-h</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--help</span>            <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show this help message and exit</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-f</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--format</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{table,json}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Output format (default: table)</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">--min-memory</span> <span style="color: #00ffff; text-decoration-color: #00ffff">MB</span>       <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Minimum memory to include (default: 5 MB)</span>
</code>
</pre>

## `kill`

```console
procclean kill --help
```

<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight"><span style="color: #00ff00; text-decoration-color: #00ff00">Usage:</span> <span style="color: #00ff00; text-decoration-color: #00ff00">procclean kill</span> [<span style="color: #00ffff; text-decoration-color: #00ffff">-h</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-f</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-y</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">--cwd</span> [<span style="color: #00ffff; text-decoration-color: #00ffff">PATH</span>]]
                      [<span style="color: #00ffff; text-decoration-color: #00ffff">-F</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{killable,orphans,high-memory}</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-k</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-o</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-m</span>]
                      [<span style="color: #00ffff; text-decoration-color: #00ffff">--min-memory</span> <span style="color: #00ffff; text-decoration-color: #00ffff">MB</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">--high-memory-threshold</span> <span style="color: #00ffff; text-decoration-color: #00ffff">MB</span>]
                      [<span style="color: #00ffff; text-decoration-color: #00ffff">--preview</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-O</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{table,json,csv,md}</span>]
                      [<span style="color: #00ffff; text-decoration-color: #00ffff">-s</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{memory,mem,cpu,pid,name,cwd}</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-n</span> <span style="color: #00ffff; text-decoration-color: #00ffff">N</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-c</span> <span style="color: #00ffff; text-decoration-color: #00ffff">COLS</span>]
                      [<span style="color: #00ffff; text-decoration-color: #00ffff">PID</span> <span style="color: #00ffff; text-decoration-color: #00ffff">...</span>]

<span style="color: #00ff00; text-decoration-color: #00ff00">Positional Arguments:</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">PID</span>                   <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Process ID(s) to kill (or use filters)</span>

<span style="color: #00ff00; text-decoration-color: #00ff00">Options:</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-h</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--help</span>            <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show this help message and exit</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-f</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--force</span>           <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Force kill (SIGKILL instead of SIGTERM)</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-y</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--yes</span>             <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Skip confirmation prompt</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">--cwd</span> [<span style="color: #00ffff; text-decoration-color: #00ffff">PATH</span>]          <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Kill processes in cwd (no value = current dir, or</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">specify path/glob)</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-F</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--filter</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{killable,orphans,high-memory}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Filter preset to select processes</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-k</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--killable</span>        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #00ffff; text-decoration-color: #00ffff">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> killable</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-o</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--orphans</span>         <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #00ffff; text-decoration-color: #00ffff">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> orphans</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-m</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--high-memory</span>     <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Shorthand for </span><span style="color: #00ffff; text-decoration-color: #00ffff">--filter</span><span style="color: #c0c0c0; text-decoration-color: #c0c0c0"> high-memory</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">--min-memory</span> <span style="color: #00ffff; text-decoration-color: #00ffff">MB</span>       <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Minimum memory for filter (default: 5 MB)</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">--high-memory-threshold</span> <span style="color: #00ffff; text-decoration-color: #00ffff">MB</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Threshold for high memory filter (default: 500 MB)</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">--preview</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--dry-run</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--dry</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Show what would be killed without killing</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-O</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--out-format</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{table,json,csv,md}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Output format for preview (default: table)</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-s</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--sort</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{memory,mem,cpu,pid,name,cwd}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Sort by field for preview</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-n</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--limit</span> <span style="color: #00ffff; text-decoration-color: #00ffff">N</span>         <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Limit preview output to N processes</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-c</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--columns</span> <span style="color: #00ffff; text-decoration-color: #00ffff">COLS</span>    <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Comma-separated columns for preview</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">(pid,name,rss_mb,cpu_percent,cwd,ppid,parent_name,stat</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">us,cmdline,username)</span>
</code>
</pre>

## `memory` / `mem`

```console
procclean memory --help
```

<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight"><span style="color: #00ff00; text-decoration-color: #00ff00">Usage:</span> <span style="color: #00ff00; text-decoration-color: #00ff00">procclean memory</span> [<span style="color: #00ffff; text-decoration-color: #00ffff">-h</span>] [<span style="color: #00ffff; text-decoration-color: #00ffff">-f</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{table,json}</span>]

<span style="color: #00ff00; text-decoration-color: #00ff00">Options:</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-h</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--help</span>            <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">show this help message and exit</span>
  <span style="color: #00ffff; text-decoration-color: #00ffff">-f</span>, <span style="color: #00ffff; text-decoration-color: #00ffff">--format</span> <span style="color: #00ffff; text-decoration-color: #00ffff">{table,json}</span>
                        <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">Output format (default: table)</span>
</code>
</pre>
