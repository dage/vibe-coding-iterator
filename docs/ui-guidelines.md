# UI Guidelines

This document establishes UI standards for the Vibe Coding Iterator project's terminal-based interfaces using the Rich library.

## Design Principles

- **Simplicity**: Clean, uncluttered interfaces that focus on essential information
- **Consistency**: Uniform styling and layout patterns across all tools
- **Readability**: High contrast and clear typography for developer workflows
- **Progressive Disclosure**: Show summary information first, details on demand
- **Minimal Color Usage**: Use white as the default text color, apply colors only to communicate specific information to users

## Color Scheme

### Default Colors
- **White**: All normal text, headers, labels, and neutral information
- **Dim**: Proprietary models, deprecated features, and secondary information

### Status Colors (Use Sparingly)
- **Green**: Success indicators and positive status
- **Yellow**: Actual warnings and rate limit notifications (not section headers)
- **Red**: Errors and critical issues

## Component Standards

### Console Output
- **Required**: Always use `console.print()` to render Rich components - they won't display without it
- **Console instance**: Create with `console = Console()` at the top of your script

### Tables
- Use `box.ROUNDED` for consistent border styling
- **Header styling**: `header_style="bold"` (default white text)
- **Column styling**: No style parameter needed (white is default)
- **Text alignment**: Right-justify numeric columns with `justify="right"`
- **Width**: Always use `width=None` for full terminal width
- **Column sizing**: Let columns auto-size with no fixed widths
- **Text wrapping**: Use `no_wrap=True` for model names and identifiers
- **Row styling**: Use `Text` objects without style parameter (white is default)

### Progress Indicators
- **Indeterminate**: Use `SpinnerColumn()` + `TextColumn()` (default white text)
- **Text format**: No color markup needed for task descriptions
- **Transient**: Use `transient=True` for temporary progress displays
- **Console**: Always pass `console=console` parameter

### Progress Bars
- **Indeterminate**: `SpinnerColumn()` + `TextColumn()` + `console=console`
- **Determinate**: Add `BarColumn()` + percentage + counts + `TimeElapsedColumn()`
- **Bar styling**: `complete_style="white"`, `finished_style="green"`
- **Text styling**: No color markup needed (default white text)
- **Width**: `width=None` and `bar_width=None` for full width
- **Task description**: Update dynamically without color markup

### Panels
- **Border style**: Always use `border_style="white"`
- **Title**: Include descriptive titles (default white text)
- **Content**: Use `Text` objects without style parameter for normal text
- **Usage**: For summaries, statistics, and key information display

### Text Styling
- **Section headers**: Use `[bold]═══ Section Name ═══[/bold]` format for component sections
- **Main titles**: Use `[bold bright_white]` for primary page titles
- **Descriptions**: Use `[dim]` for secondary descriptive text
- **Normal text**: No style parameter needed (default white text)
- **Model identifiers**: Use `style="cyan"` for model names and identifiers (e.g., "meta-llama/CodeLlama-7b")
- **Numbers and metrics**: Use `style="bright_blue"` for numerical values, counts, and percentages (e.g., downloads, likes, percentages)
- **Rate limit numbers**: Use `style="yellow"` when numbers are part of warning messages (e.g., "Rate limit: 80/100")
- **Prompts and instructions**: Use `style="bright_white"` for AI prompts and user instructions
- **Proprietary models**: Use `style="dim"` for unavailable/limited models
- **Explanatory text**: Use `style="italic"` for notes and explanations
- **Status indicators**: Use appropriate status colors (green/yellow/red) sparingly
- **Success completion**: Use `[bold green]` for final success messages (e.g., "✓ All UI components tested successfully!")
- **Tag limits**: Display maximum 5 most relevant tags per model

## Layout Patterns

### Model Lists
1. **Header**: Clear title with model count in format `"Model Analysis - {name} ({count} models)"`
2. **Table**: Model name, tags, metrics, dates, author, status columns
3. **Summary**: Total counts and categorization breakdown in panel

### Error Handling
- **Error messages**: Use `style="red"` with clear descriptions
- **Warning messages**: Use `style="yellow"` with actionable guidance
- **Success messages**: Use `style="green"` for successful operations
- **Progress indicators**: Show retry attempts with spinners

### Rate Limiting
- **Notifications**: Use `style="yellow"` for rate limit warnings
- **Progress**: Continue showing progress during delays
- **User feedback**: Clear messaging about wait times and retries

### Status Messages
- **Format**: Use consistent prefix symbols: `✗` for errors, `⚠` for warnings, `✓` for success
- **Styling**: Combine symbols with appropriate colors (default white text)
- **Placement**: Display after main content, before rate limiting demos

## Example Usage

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

# Create table with consistent styling
table = Table(
    title="Model Analysis - Clean Professional (4 models)",
    box=box.ROUNDED,
    show_header=True,
    header_style="bold",
    width=None
)

# Add columns with appropriate styling
table.add_column("Model", no_wrap=True)
table.add_column("Tags")
table.add_column("Downloads", justify="right")
table.add_column("Likes", justify="right")
table.add_column("Updated")
table.add_column("Author")
table.add_column("Status")

# Add rows with conditional styling
table.add_row(
    Text("meta-llama/CodeLlama-7b", style="cyan"),
    Text("code, instruct"),
    Text("2.1M", style="bright_blue"),
    Text("1.2K", style="bright_blue"),
    Text("2024-01-15"),
    Text("Meta"),
    Text("Active", style="green")
)

# Display with summary panel
summary_text = Text()
summary_text.append("Total Models: ")
summary_text.append("4", style="bright_blue")
summary_text.append(" | Active: ")
summary_text.append("2", style="green")

console.print(table)
console.print(Panel(summary_text, title="Summary", border_style="white"))
``` 