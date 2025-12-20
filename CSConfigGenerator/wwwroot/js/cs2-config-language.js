// CS2 Config Language for Monaco Editor
// Provides intellisense (autocomplete + hover) for CS2 console commands

(function () {
    'use strict';

    // Store command data passed from Blazor
    let commandData = [];
    let commandMap = new Map();
    let isLanguageRegistered = false;

    /**
     * Initialize the CS2 config language with command data.
     * Called from Blazor via JS interop.
     * @param {Array} commands - Array of command objects with: command, type, description, defaultValue, range, isCheat
     */
    window.initCs2ConfigLanguage = function (commands) {
        if (!commands || !Array.isArray(commands)) {
            console.warn('initCs2ConfigLanguage: No commands provided');
            return;
        }

        commandData = commands;
        commandMap.clear();

        // Build lookup map for hover provider
        for (const cmd of commands) {
            commandMap.set(cmd.command.toLowerCase(), cmd);
        }

        // Register language only once
        if (!isLanguageRegistered) {
            registerLanguage();
            isLanguageRegistered = true;
        }

        console.log(`CS2 Config language initialized with ${commands.length} commands`);
    };

    /**
     * Register the cs2config language with Monaco
     */
    function registerLanguage() {
        // Register the language
        monaco.languages.register({ id: 'cs2config' });

        // Set language configuration (comments, brackets, etc.)
        monaco.languages.setLanguageConfiguration('cs2config', {
            comments: {
                lineComment: '//'
            },
            brackets: [
                ['"', '"']
            ],
            autoClosingPairs: [
                { open: '"', close: '"' }
            ],
            surroundingPairs: [
                { open: '"', close: '"' }
            ]
        });

        // Register completion provider
        monaco.languages.registerCompletionItemProvider('cs2config', {
            triggerCharacters: [],
            provideCompletionItems: provideCompletionItems
        });

        // Register hover provider
        monaco.languages.registerHoverProvider('cs2config', {
            provideHover: provideHover
        });
    }

    /**
     * Provide autocomplete suggestions
     */
    function provideCompletionItems(model, position) {
        // Get the text on the current line up to the cursor
        const lineContent = model.getLineContent(position.lineNumber);
        const textUntilPosition = lineContent.substring(0, position.column - 1);

        // Find the word being typed (start of line or after whitespace/semicolon)
        const wordMatch = textUntilPosition.match(/(?:^|[\s;])([^\s;]*)$/);
        const currentWord = wordMatch ? wordMatch[1].toLowerCase() : '';

        // Get the word range for replacement
        const wordInfo = model.getWordUntilPosition(position);
        const range = {
            startLineNumber: position.lineNumber,
            startColumn: wordInfo.startColumn,
            endLineNumber: position.lineNumber,
            endColumn: wordInfo.endColumn
        };

        // Filter commands that match the current word
        const suggestions = [];

        for (const cmd of commandData) {
            const cmdLower = cmd.command.toLowerCase();

            // Match if word is empty (show all) or command starts with the word
            if (currentWord === '' || cmdLower.startsWith(currentWord)) {
                suggestions.push(createCompletionItem(cmd, range));
            }
        }

        return { suggestions: suggestions };
    }

    /**
     * Create a completion item for a command
     */
    function createCompletionItem(cmd, range) {
        // Determine the kind based on type
        const isCommand = cmd.type === 'command';
        const kind = isCommand
            ? monaco.languages.CompletionItemKind.Function
            : monaco.languages.CompletionItemKind.Variable;

        // Build detail string (type info)
        let detail = cmd.type;
        if (cmd.range) {
            detail += ` [${cmd.range}]`;
        }
        if (cmd.defaultValue) {
            detail += ` = ${cmd.defaultValue}`;
        }
        if (cmd.isCheat) {
            detail += ' (cheat)';
        }

        // For cvars (non-commands), add a space after insertion to encourage value entry
        const insertText = isCommand ? cmd.command : cmd.command + ' ';

        return {
            label: cmd.command,
            kind: kind,
            detail: detail,
            documentation: cmd.description || undefined,
            insertText: insertText,
            range: range,
            sortText: cmd.command.toLowerCase()
        };
    }

    /**
     * Provide hover information for commands
     */
    function provideHover(model, position) {
        // Get the word at the current position
        const wordInfo = model.getWordAtPosition(position);
        if (!wordInfo) {
            return null;
        }

        const word = wordInfo.word.toLowerCase();
        const cmd = commandMap.get(word);

        if (!cmd) {
            return null;
        }

        // Build hover content
        const contents = [];

        // Command name with type
        let header = `**${cmd.command}**`;
        if (cmd.type) {
            header += ` *(${cmd.type})*`;
        }
        contents.push({ value: header });

        // Type details
        const details = [];
        if (cmd.range) {
            details.push(`Range: ${cmd.range}`);
        }
        if (cmd.defaultValue) {
            details.push(`Default: ${cmd.defaultValue}`);
        }
        if (cmd.isCheat) {
            details.push('⚠️ Requires sv_cheats 1');
        }

        if (details.length > 0) {
            contents.push({ value: details.join(' | ') });
        }

        // Description
        if (cmd.description) {
            contents.push({ value: cmd.description });
        }

        return {
            range: {
                startLineNumber: position.lineNumber,
                startColumn: wordInfo.startColumn,
                endLineNumber: position.lineNumber,
                endColumn: wordInfo.endColumn
            },
            contents: contents
        };
    }

})();
