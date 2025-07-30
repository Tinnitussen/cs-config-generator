## This are the automatic type parsing rules:

1. A command is an action if its defaultValue is null.
1. A command is a bool if its defaultValue is "true" or "false". We do not infer booleans from 0/1.
1. A command is a bitmask if its description explicitly contains the word "bitmask".
1. A command is a float if its defaultValue is a numeric string that contains a decimal point.
1. A command is an unknown_numeric if its defaultValue is a numeric string without a decimal point.
1. A command is a string if its defaultValue is not null, not a boolean, and not numeric.