This was meant to be a simple script that I might use once. Then it got complicated. It is no longer that simple a script.

The idea was that sometimes when updating requirements files, some dependency of some dependency would break and things would stop passing tests. Sometimes it isn't obvious what's causing the failure, and there can be a _lot_ of updates if you're not running dependabot, updating regularly enough, etc. Thus, I wanted a tool that would go through the requirements and do something like a bisect testing to find what requirement or requirements are causing tests to file. Easy, right?

Well, this is my work in progress of that idea.
It will probably never get finished.
