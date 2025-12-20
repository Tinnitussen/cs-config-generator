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

        // Register Monarch tokenizer for syntax highlighting
        // Design: Quotes are optional in CS2 configs, so "0.01" and 0.01 are the same.
        // We use 'string' for all values (quoted or numeric) so they appear consistently.
        monaco.languages.setMonarchTokensProvider('cs2config', {
            tokenizer: {
                root: [
                    [/\/\/.*$/, 'comment'],              // Comments
                    [/"[^"]*"/, 'string'],               // Quoted values (e.g., "255", "+forward")
                    [/"[^"]*$/, 'string.invalid'],       // Unclosed quote (visual error indicator)
                    [/\b-?\d+\.?\d*\b/, 'string'],       // Numeric values - same style as quoted
                    [/\b(bind|unbind|alias|exec|echo|toggle|incrementvar|say)\b/i, 'keyword'],
                    [/[a-zA-Z_][\w]*/, 'identifier'],    // Command/cvar names
                    [/;/, 'delimiter'],                  // Semicolon command separator
                ]
            }
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

    /**
     * Validate the document and set error/warning markers.
     * Called on document change to provide live feedback.
     * @param {object} model - Monaco editor text model
     */
    function validateDocument(model) {
        const markers = [];
        const lineCount = model.getLineCount();

        // First pass: collect all alias definitions
        const definedAliases = new Set();
        for (let lineNumber = 1; lineNumber <= lineCount; lineNumber++) {
            const lineContent = model.getLineContent(lineNumber);
            // Match alias definitions: alias "name" ... or alias name ...
            const aliasMatch = lineContent.match(/^\s*alias\s+(?:"([^"]+)"|(\S+))/i);
            if (aliasMatch) {
                const aliasName = (aliasMatch[1] || aliasMatch[2]).toLowerCase();
                definedAliases.add(aliasName);
            }
        }

        // Second pass: validate each line
        for (let lineNumber = 1; lineNumber <= lineCount; lineNumber++) {
            const lineContent = model.getLineContent(lineNumber);
            const lineMarkers = validateLine(lineContent, lineNumber, definedAliases);
            markers.push(...lineMarkers);
        }

        // Set the markers on the model
        monaco.editor.setModelMarkers(model, 'cs2config', markers);
    }

    /**
     * Validate a single line and return markers for any issues.
     * @param {string} lineContent - The line text
     * @param {number} lineNumber - 1-based line number
     * @param {Set} definedAliases - Set of alias names defined in the document
     * @returns {Array} Array of marker objects
     */
    function validateLine(lineContent, lineNumber, definedAliases) {
        const markers = [];
        const trimmed = lineContent.trim();

        // Skip empty lines and comments
        if (trimmed === '' || trimmed.startsWith('//')) {
            return markers;
        }

        // Remove trailing comment for validation
        const commentIndex = lineContent.indexOf('//');
        const codeContent = commentIndex >= 0 ? lineContent.substring(0, commentIndex) : lineContent;

        // Check for unclosed quotes
        const unclosedQuoteMarker = checkUnclosedQuote(codeContent, lineNumber);
        if (unclosedQuoteMarker) {
            markers.push(unclosedQuoteMarker);
            // Don't do further validation if there's an unclosed quote
            return markers;
        }

        // Split by semicolons to handle multiple commands on one line
        const commands = splitCommands(codeContent);

        for (const cmd of commands) {
            const commandMarker = validateCommand(cmd.text, lineNumber, cmd.startColumn, definedAliases);
            if (commandMarker) {
                markers.push(commandMarker);
            }
        }

        return markers;
    }

    /**
     * Check for unclosed quotes in a line.
     * @returns {object|null} Marker object or null if no issue
     */
    function checkUnclosedQuote(lineContent, lineNumber) {
        let inQuote = false;
        let quoteStart = 0;

        for (let i = 0; i < lineContent.length; i++) {
            if (lineContent[i] === '"') {
                if (!inQuote) {
                    inQuote = true;
                    quoteStart = i;
                } else {
                    inQuote = false;
                }
            }
        }

        if (inQuote) {
            return {
                severity: monaco.MarkerSeverity.Error,
                message: 'Unclosed quote',
                startLineNumber: lineNumber,
                startColumn: quoteStart + 1,  // Monaco uses 1-based columns
                endLineNumber: lineNumber,
                endColumn: lineContent.length + 1
            };
        }

        return null;
    }

    /**
     * Split a line into individual commands (separated by semicolons outside quotes).
     * @returns {Array} Array of {text, startColumn} objects
     */
    function splitCommands(lineContent) {
        const commands = [];
        let current = '';
        let currentStart = 0;
        let inQuote = false;

        for (let i = 0; i < lineContent.length; i++) {
            const char = lineContent[i];

            if (char === '"') {
                inQuote = !inQuote;
                current += char;
            } else if (char === ';' && !inQuote) {
                if (current.trim()) {
                    commands.push({ text: current, startColumn: currentStart + 1 });
                }
                current = '';
                currentStart = i + 1;
            } else {
                current += char;
            }
        }

        // Don't forget the last command
        if (current.trim()) {
            commands.push({ text: current, startColumn: currentStart + 1 });
        }

        return commands;
    }

    /**
     * Validate a single command and return a marker if it's unknown.
     * @returns {object|null} Marker object or null if valid
     */
    function validateCommand(commandText, lineNumber, startColumn, definedAliases) {
        const trimmed = commandText.trim();
        if (!trimmed) {
            return null;
        }

        // Extract the command name (first word, possibly quoted)
        let commandName;
        const match = trimmed.match(/^(?:"([^"]+)"|(\S+))/);
        if (!match) {
            return null;
        }
        commandName = (match[1] || match[2]).toLowerCase();

        // Check if it's a known command, alias, or +/- prefixed command
        if (commandMap.has(commandName)) {
            return null;  // Known command
        }

        // Check +/- variants (e.g., +forward, -forward)
        if (commandName.startsWith('+') || commandName.startsWith('-')) {
            const baseCmd = commandName.substring(1);
            if (commandMap.has('+' + baseCmd) || commandMap.has('-' + baseCmd) || commandMap.has(baseCmd)) {
                return null;
            }
        }

        // Check defined aliases
        if (definedAliases.has(commandName)) {
            return null;  // User-defined alias
        }

        // Find the position of the command name in the original text
        const cmdStartInText = commandText.indexOf(match[0]);
        const cmdEndColumn = startColumn + cmdStartInText + match[0].length;

        return {
            severity: monaco.MarkerSeverity.Warning,
            message: `Unknown command: ${match[1] || match[2]}`,
            startLineNumber: lineNumber,
            startColumn: startColumn + cmdStartInText,
            endLineNumber: lineNumber,
            endColumn: cmdEndColumn
        };
    }

    /**
     * Set up validation for an editor instance.
     * Called from Blazor after editor is created.
     * @param {string} editorId - The container ID of the editor
     */
    window.setupCs2ConfigValidation = function (editorId) {
        // Find the editor by looking for Monaco editors
        const editors = monaco.editor.getEditors();
        
        for (const editor of editors) {
            const container = editor.getContainerDomNode();
            if (container && container.closest('#' + editorId)) {
                const model = editor.getModel();
                if (model) {
                    // Initial validation
                    validateDocument(model);

                    // Validate on content change (debounced)
                    let validationTimeout = null;
                    editor.onDidChangeModelContent(() => {
                        if (validationTimeout) {
                            clearTimeout(validationTimeout);
                        }
                        validationTimeout = setTimeout(() => {
                            validateDocument(model);
                        }, 300);  // 300ms debounce
                    });

                    console.log('CS2 config validation set up for editor');
                    return true;
                }
            }
        }

        console.warn('setupCs2ConfigValidation: Editor not found for id:', editorId);
        return false;
    };

})();
