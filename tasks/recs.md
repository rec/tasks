### Record incoming keystrokes and save in manifest

A new enum config: `record_keys`: 'none', 'press', 'all'

A new bool config: `record_key_all_apps`.

There are three cases:

1. Pyside6:

If `record_keys` is not set, it defaults to `all`.
If  `record_key_all_apps` is not set, it defaults to True.
`pyinput` is not used at all.

2. A terminal where pynput works

If `record_keys` is not set, it defaults to `all`.
If  `record_key_all_apps` is not set, it defaults to `record_key != all`

3. A terminal where it doesn't work

If `record_keys` is not set, it defaults to `press`.
`record_keys` cannot be `all`.
`record_key_all_apps` must be False

### Split the something.
