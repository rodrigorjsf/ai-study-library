# Command palette and chords

Cmd/Ctrl+K palette family (global, actions, files, threads, settings) and go-to-thread number chords.

## Sub-features

- global-palette: Cmd/Ctrl+K command palette
- files-palette: file picker flavor of the palette
- threads-palette: jump to thread by name
- shortcuts-help: keyboard shortcuts help overlay
- go-to-thread-chords: Cmd/Ctrl+1..9 jump to recent threads

## How to get to it (user POV)

Press Cmd/Ctrl+K from most surfaces. Inside settings, the same chord is preferences search (see `preferences.md`).

Open Shortcuts from the account menu or the help entry in the palette.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs press "Meta+KeyK"
node .cursor/skills/verify-atlas/control-atlas.mjs type "new thread"
node .cursor/skills/verify-atlas/control-atlas.mjs press "Enter"
```

Assert the palette dialog in the a11y tree before typing. Escape closes without action.

Go-to-thread: press Meta+Digit1 after establishing at least one recent thread; assert selection changed.

## Gotchas

- Focus context changes what Cmd/Ctrl+K does. Establish surface first.
- Number chords no-op when fewer threads exist than the digit. Seed rows first.
