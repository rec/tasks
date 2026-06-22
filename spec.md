# pop_task pops a task, prints it, and saves it.

Take the existing `/Users/tom/code/dotfiles/bin/pop_task` and change it as little as possible
and write it here in `/Users/tom/code/tasks/pop_task`

When this new `pop_task` is executed in a project:

1. It gets the name of the top-level directory of the project (e.g. `tuney`)
2. It looks at the file in this directory of the same name (e.g. `tuney.md`)
3. It pops any empty tasks, pops off the first non-empty task, and prints it.
4. It then prints the remaining file back, and appends the removed task to the file of the same name in 'done/', creating it if necessary.
