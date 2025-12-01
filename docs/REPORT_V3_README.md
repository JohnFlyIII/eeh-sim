# Enhanced HTML Reports for EEH v3

## Overview

The v3 reporting system generates publication-quality HTML reports with modern styling, interactive visualizations, and clear demonstration of the Ethical Event Horizon differential.

## What's New in V3 Reports

### 🎨 **Modern Design**
- Responsive CSS grid layout
- Professional color scheme with proper contrast
- Side-by-side agent comparisons
- Mobile-friendly responsive design
- Clean typography and spacing

### 📊 **Enhanced Visualizations**

**1. Temporal Causal Chains**
- Hierarchical left-to-right layout (temporal flow)
- Color-coded nodes:
  - 🔴 Red: Root causes (bar, alcohol, sleep deprivation)
  - 🟡 Yellow: Intermediate factors
  - 🔵 Blue: Outcomes (collision, detection failure)
- Temporal annotations showing hours before collision
- Text wrapping for long labels (no more overlap!)

**2. Comparison Dashboard**
- 6-panel comparison showing:
  - Chain depth (actual vs expected)
  - Temporal span (hours traced back)
  - Decision match indicators
  - Root causes identified
  - Decision text comparison
  - Overall EEH status

**3. Temporal Depth Timeline**
- Visual timeline showing how far back each agent traces
- Clear visualization of 0h (human) vs 5+h (ASI)
- Annotations explaining the differential

**4. Decision Comparison**
- Side-by-side decision display
- Expected vs actual with ✓/✗ indicators
- Color-coded match status

### 🎯 **EEH Highlighting**
- Dedicated section explaining the Ethical Event Horizon
- Yellow callout box with clear explanation
- Status banner showing if EEH was successfully demonstrated

## Usage

### Automatic Generation

When you run `./scripts/run_v3.sh`, the HTML report is automatically generated:

```bash
./scripts/run_v3.sh

# Output includes:
# runs/no_fault_v3_20251102_235053.json
# runs/no_fault_v3_20251102_235053.html  ← Auto-generated!
# runs/figs_v3/  ← Enhanced visualizations
```

### Manual Generation

Generate report from existing JSON:

```bash
# Basic usage (output: same name with .html)
python generate_report_v3.py runs/no_fault_v3_20251102_235053.json

# Custom output path
python generate_report_v3.py runs/my_results.json --output reports/analysis.html

# View in browser
open runs/no_fault_v3_20251102_235053.html  # macOS
xdg-open runs/no_fault_v3_20251102_235053.html  # Linux
```

## Output Structure

```
runs/
├── no_fault_v3_20251102_235053.json         # Raw results
├── no_fault_v3_20251102_235053.html         # Enhanced HTML report
└── figs_v3/                                  # Visualization assets
    ├── temporal_chain_human.png              # Human causal chain
    ├── temporal_chain_asi.png                # ASI causal chain
    ├── comparison_dashboard.png              # 6-panel comparison
    ├── temporal_depth_comparison.png         # Timeline view
    └── decision_comparison.png               # Decision attribution
```

## Comparison: V2 vs V3 Reports

| Feature | V2 Reports | V3 Reports |
|---------|-----------|------------|
| **Layout** | Basic stacked images | Modern CSS grid, side-by-side |
| **Causal Graphs** | Spring layout (messy) | Hierarchical temporal flow |
| **Node Colors** | Single color | Color-coded by type (root/intermediate/outcome) |
| **Text Overlap** | ❌ Severe overlap | ✅ Wrapped labels, no overlap |
| **Temporal Info** | None visible | Timeline with hour annotations |
| **Comparison View** | Separate images | Integrated dashboard |
| **EEH Explanation** | None | Dedicated explanation section |
| **Status Indicator** | None | Color-coded status banner |
| **Responsive** | No | Yes |
| **Publication-Ready** | No | Yes |

## Requirements

### Standard
- Python 3.8+
- matplotlib
- networkx
- rich (for CLI output)

### Optional (for better graph layouts)
- pygraphviz (enables hierarchical layout)
- graphviz system library

**Install with:**
```bash
pip install matplotlib networkx rich

# Optional (for best layouts):
# macOS:
brew install graphviz
pip install pygraphviz

# Linux:
sudo yum install graphviz-devel
pip install pygraphviz
```

If pygraphviz is not available, the system falls back to spring layout (still better than v2).

## Customization

### Modify Colors

Edit `src/eeh_llm/plots_v3.py`:

```python
# Root cause color (currently red)
node_colors.append('#ef4444')

# Intermediate color (currently yellow)
node_colors.append('#fbbf24')

# Outcome color (currently blue)
node_colors.append('#3b82f6')
```

### Modify HTML Styling

Edit `src/eeh_llm/report_v3.py`:

```python
# Look for the <style> section
# Modify colors, fonts, spacing, etc.
```

### Add Custom Sections

In `report_v3.py`, add new sections to `_build_html_content()`:

```python
# Add custom analysis section
<div class="section">
    <h2>Your Custom Section</h2>
    <p>Your content here</p>
</div>
```

## Publishing Reports

The generated HTML reports are self-contained and publication-ready:

1. **For papers**: Include figures from `figs_v3/` directory
2. **For web**: Upload the entire directory (HTML + figs_v3/)
3. **For presentations**: Screenshots of the HTML render beautifully

## Troubleshooting

### "HTML report generation failed"

**Cause**: Missing matplotlib or other dependencies

**Fix**:
```bash
pip install matplotlib networkx rich
```

### Graph labels still overlap

**Cause**: pygraphviz not installed (using spring layout fallback)

**Fix**: Install pygraphviz for hierarchical layout (see Requirements above)

### Figures not showing in HTML

**Cause**: Relative paths broken if HTML moved

**Fix**: Keep HTML and `figs_v3/` folder together, or regenerate report in new location

### Colors look wrong

**Cause**: Browser CSS caching

**Fix**: Hard refresh (Cmd+Shift+R on macOS, Ctrl+Shift+R on Linux/Windows)

## Examples

### Generate Report for Latest Run
```bash
# Find latest v3 JSON
LATEST=$(ls -t runs/no_fault_v3_*.json | head -1)

# Generate report
python generate_report_v3.py "$LATEST"

# Open in browser
open "${LATEST%.json}.html"
```

### Batch Generate Reports
```bash
# Generate reports for all v3 results
for json in runs/*_v3_*.json; do
    python generate_report_v3.py "$json"
done
```

### Compare Multiple Runs
```bash
# Generate reports with custom names
python generate_report_v3.py runs/run1.json --output reports/7B_model.html
python generate_report_v3.py runs/run2.json --output reports/32B_model.html
```

## Citation

When using these reports in publications, please cite:

```
Fly, J. B. III (2025). The Ethical Event Horizon: Understanding Intelligence
Differentials in Ethical Comprehension. Journal of Ethics and the Law Today,
2(4), 1-32.
```

## Future Enhancements

Potential improvements for future versions:

- [ ] Interactive D3.js graphs (hover for details)
- [ ] Animated temporal flow visualization
- [ ] Export to PDF
- [ ] Comparative analysis across multiple runs
- [ ] Statistical significance testing
- [ ] Dark mode toggle
- [ ] Embed videos/animations

## Support

For issues or questions about the reporting system:
- Check existing v3 results for examples
- Review matplotlib/networkx documentation for graph customization
- Open an issue in the repository
