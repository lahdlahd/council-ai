# STAGE 2 — UI/UX SYSTEM
## Council: Design System & Specifications

**Status**: UI/UX Design (No Code)  
**Version**: 1.0  
**Date**: June 12, 2026  
**Aesthetic**: Bloomberg Terminal × BlackRock × Institutional Finance

---

## 1. DESIGN SYSTEM OVERVIEW

### 1.1 Design Philosophy

**Council** should feel like:
- Premium institutional trading platform
- High-information density without chaos
- Dark theme (professional, focus-inducing)
- Minimal ornamentation (form over decoration)
- Data-forward (charts and metrics dominate)
- Serious (not playful or trendy)

**Core Principles:**
- **Clarity**: Every element has a clear purpose
- **Hierarchy**: Information priority is visually obvious
- **Constraint**: Limited palette creates sophistication
- **Precision**: Pixel-perfect alignment
- **Contrast**: Dark backgrounds with strategic accent colors
- **Density**: More information per screen, less scrolling
- **Consistency**: Unified component language across all screens

### 1.2 Design System Layers

```
Foundation Layer (Colors, Typography, Icons)
        ↓
Component Layer (Buttons, Cards, Inputs, Charts)
        ↓
Pattern Layer (Headers, Sidebars, Modals, Forms)
        ↓
Screen Layer (Dashboard, Council Chamber, Portfolio)
        ↓
Interaction Layer (Animations, Transitions, Feedback)
```

---

## 2. COLOR SYSTEM

### 2.1 Core Color Palette

**Primary Colors** (UI structure, backgrounds):
```
Primary Dark:    #111315  - Main background
Primary Medium:  #1B1F24  - Secondary surfaces
Primary Light:   #2A3035  - Interactive elements on dark bg
```

**Accent Color** (Premium, investment focus):
```
Accent Gold:     #D4A24C  - Primary action, highlights, premium feel
Accent Gold 80%: #E0B566  - Hover states, lighter variant
Accent Gold 60%: #D9AF7A  - Secondary accent
```

**Status Colors**:
```
Success Green:   #1D9B72  - Positive movements, buy signals, approvals
Warning Orange:  #C98A21  - Caution, hold signals, alerts
Danger Red:      #A84747  - Negative movements, sell signals, errors
```

**Neutral/Utility**:
```
Text Primary:    #FFFFFF  - Main text, high contrast
Text Secondary:  #9FA3A8  - Supporting text, labels
Text Tertiary:   #6D7175  - Disabled, hints
Border Dark:     #3A3F45  - Strong dividers
Border Light:    #2A3035  - Subtle dividers
```

### 2.2 Color Application Guide

**Backgrounds**:
- Page background: `#111315`
- Card/Panel background: `#1B1F24`
- Elevated surface: `#2A3035`
- Hover state: `rgba(212, 162, 76, 0.08)` (subtle accent overlay)

**Text**:
- Primary text (body): `#FFFFFF`
- Secondary text (labels): `#9FA3A8`
- Disabled text: `#6D7175`
- Link text: `#D4A24C` (accent gold)

**Interactive Elements**:
- Primary button: `#D4A24C` background, `#111315` text
- Secondary button: `#2A3035` background, `#D4A24C` border, `#FFFFFF` text
- Hover state: Brighten accent by +10%
- Active state: Accent with `rgba(212, 162, 76, 0.2)` underlay

**Data Visualization**:
- Bullish/Long: `#1D9B72` (success green)
- Bearish/Short: `#A84747` (danger red)
- Neutral: `#6D7175` (text tertiary)
- Volume bars: `rgba(212, 162, 76, 0.4)` (accent with transparency)

**Charts**:
- Candlestick up: `#1D9B72`
- Candlestick down: `#A84747`
- Grid lines: `#2A3035`
- Background: `#111315`
- Text: `#9FA3A8`

### 2.3 Color Accessibility

- All text meets WCAG AA contrast ratios
- Success/Error never sole differentiator
- Color blindness support (distinct symbols)
- High contrast mode supported

---

## 3. TYPOGRAPHY SYSTEM

### 3.1 Font Stack

**Primary Font**: Inter
- Clean, modern, excellent screen readability
- Available on Google Fonts
- Used for: Body text, UI labels, interface

**Secondary Font**: IBM Plex Mono
- Monospaced for data/numbers
- Professional, technical feel
- Used for: Prices, timestamps, metrics, code

**Fallback Stack**:
```
Display: Inter, -apple-system, BlinkMacSystemFont, sans-serif
Mono: "IBM Plex Mono", "Courier New", monospace
```

### 3.2 Type Scale

**Display (Headlines)**:
```
Display Large (48px):
- Font: Inter Bold
- Weight: 700
- Line height: 1.2
- Letter spacing: -0.5px
- Use: Page titles

Display Medium (36px):
- Font: Inter Bold
- Weight: 700
- Line height: 1.2
- Letter spacing: -0.3px
- Use: Section titles

Display Small (28px):
- Font: Inter SemiBold
- Weight: 600
- Line height: 1.3
- Letter spacing: 0px
- Use: Subsection titles
```

**Heading (Sections)**:
```
Heading 1 (24px):
- Font: Inter SemiBold
- Weight: 600
- Line height: 1.4
- Letter spacing: 0px
- Use: Card headers, modal titles

Heading 2 (20px):
- Font: Inter SemiBold
- Weight: 600
- Line height: 1.4
- Letter spacing: 0px
- Use: Subsection headers

Heading 3 (16px):
- Font: Inter Medium
- Weight: 500
- Line height: 1.5
- Letter spacing: 0px
- Use: Component headers, labels
```

**Body (Content)**:
```
Body Large (16px):
- Font: Inter Regular
- Weight: 400
- Line height: 1.6
- Letter spacing: 0px
- Use: Primary body text, descriptions

Body Regular (14px):
- Font: Inter Regular
- Weight: 400
- Line height: 1.6
- Letter spacing: 0px
- Use: Standard body, form fields

Body Small (12px):
- Font: Inter Regular
- Weight: 400
- Line height: 1.5
- Letter spacing: 0px
- Use: Helper text, timestamps
```

**Data/Numbers**:
```
Numeric Large (16px):
- Font: IBM Plex Mono
- Weight: 400
- Line height: 1.6
- Letter spacing: 0px
- Use: Price displays, large metrics

Numeric Regular (14px):
- Font: IBM Plex Mono
- Weight: 400
- Line height: 1.6
- Letter spacing: 0px
- Use: Standard data, table cells

Numeric Small (12px):
- Font: IBM Plex Mono
- Weight: 400
- Line height: 1.5
- Letter spacing: 0px
- Use: Small metrics, hints
```

**Labels & Tags**:
```
Label (12px):
- Font: Inter SemiBold
- Weight: 600
- Line height: 1.5
- Letter spacing: 0.5px
- Text transform: UPPERCASE
- Use: Field labels, tags, badges

Caption (11px):
- Font: Inter Medium
- Weight: 500
- Line height: 1.5
- Letter spacing: 0.3px
- Use: Captions, helper text
```

### 3.3 Font Weight Distribution

- **700 Bold**: Display headlines only
- **600 SemiBold**: Headings, emphasis, important labels
- **500 Medium**: UI labels, emphasis in body
- **400 Regular**: Body text, most content

---

## 4. SPACING & LAYOUT GRID

### 4.1 Spacing Scale

**Base Unit**: 4px (provides flexibility while maintaining consistency)

```
Spacing Scale:
xs:   4px    (0.25rem)  - Tight spacing, internal component
sm:   8px    (0.5rem)   - Small gaps, component internals
md:   12px   (0.75rem)  - Medium spacing, standard padding
lg:   16px   (1rem)     - Large spacing, section gaps
xl:   24px   (1.5rem)   - Extra large, major sections
xxl:  32px   (2rem)     - Page margins, major dividers
3xl:  48px   (3rem)     - Page sections
4xl:  64px   (4rem)     - Rare, special cases
```

### 4.2 Layout Grid

**Desktop Grid** (1440px viewport):
```
12-column grid
Column width: 92px
Gutter: 24px
Margin: 32px (left & right)

Total usable width: 1376px (1440 - 64)
```

**Grid Application**:
- Sidebar: 3 columns (292px)
- Main content: 9 columns (1084px)
- Gutter between: 24px

**Breakpoints**:
```
Mobile:     320px - 639px
Tablet:     640px - 1023px
Desktop:    1024px - 1439px
Large:      1440px - 1919px
XL:         1920px+
```

### 4.3 Component Sizing

**Heights**:
```
Controls:
- xs button:     24px (padding: 4px 12px)
- sm button:     32px (padding: 8px 16px)
- md button:     40px (padding: 12px 20px)
- lg button:     48px (padding: 16px 24px)

Input fields:
- Compact:       32px
- Standard:      40px
- Spacious:      48px

Cards:
- Minimum:       120px
- Standard:      240px
- Large:         360px+
```

**Widths**:
```
Modals:
- Small:   480px
- Medium:  720px
- Large:   960px

Panels:
- Sidebar: 292px
- Mini:    240px
- Wide:    360px
```

---

## 5. COMPONENT SYSTEM

### 5.1 Core Components

**Buttons**:
```
Primary Button:
- Background: #D4A24C
- Text: #111315 (bold, semibold)
- Padding: 12px 20px
- Border radius: 4px
- Hover: #E0B566
- Active: #C4962E
- Disabled: #6D7175 with 50% opacity

Secondary Button:
- Background: transparent
- Border: 1px #D4A24C
- Text: #D4A24C
- Padding: 12px 20px
- Border radius: 4px
- Hover: background #D4A24C, text #111315
- Active: Darker accent

Ghost Button:
- Background: transparent
- Text: #9FA3A8
- Padding: 12px 20px
- Hover: text #FFFFFF
- Active: text #D4A24C

Danger Button:
- Background: #A84747
- Text: #FFFFFF
- Similar behavior to primary
```

**Input Fields**:
```
Text Input:
- Background: #1B1F24
- Border: 1px #3A3F45
- Text: #FFFFFF
- Placeholder: #6D7175
- Padding: 12px 16px
- Border radius: 4px
- Focus: Border #D4A24C, box-shadow none
- Error: Border #A84747

Select:
- Same styling as text input
- Icon: #9FA3A8 (right-aligned)
- Options background: #2A3035

Checkbox:
- Size: 16px × 16px
- Unchecked: border #3A3F45
- Checked: background #D4A24C
- Border radius: 2px

Radio:
- Size: 16px × 16px
- Unchecked: border #3A3F45
- Checked: background #D4A24C
- Border radius: 50%
```

**Cards**:
```
Standard Card:
- Background: #1B1F24
- Border: 1px #3A3F45
- Border radius: 4px
- Padding: 16px
- Hover: Border #D4A24C (optional)
- Shadow: none (flat design)

Elevated Card:
- Same as standard
- Subtle background: #2A3035
- Border: 1px #2A3035

Interactive Card:
- Cursor: pointer
- Hover: Border #D4A24C, background slightly lighter
```

**Badges/Tags**:
```
Success Badge:
- Background: rgba(29, 155, 114, 0.15)
- Text: #1D9B72
- Padding: 4px 8px
- Border radius: 4px
- Font size: 12px

Warning Badge:
- Background: rgba(201, 138, 33, 0.15)
- Text: #C98A21
- Padding: 4px 8px
- Border radius: 4px

Danger Badge:
- Background: rgba(168, 71, 71, 0.15)
- Text: #A84747
- Padding: 4px 8px
- Border radius: 4px

Neutral Badge:
- Background: #2A3035
- Text: #9FA3A8
- Padding: 4px 8px
- Border radius: 4px
```

**Tabs**:
```
Tab Container:
- Background: transparent
- Border bottom: 1px #3A3F45

Tab Item (Inactive):
- Color: #9FA3A8
- Border bottom: 2px transparent
- Padding: 12px 16px
- Hover: color #FFFFFF

Tab Item (Active):
- Color: #D4A24C
- Border bottom: 2px #D4A24C
- Padding: 12px 16px
```

**Dividers**:
```
Horizontal Divider:
- Height: 1px
- Color: #3A3F45
- Margin: 16px 0 (or configurable)

Vertical Divider:
- Width: 1px
- Color: #3A3F45
- Margin: 0 16px (or configurable)

Subtle Divider:
- Color: #2A3035
```

**Lists**:
```
List Item:
- Padding: 12px 16px
- Background: transparent
- Border bottom: 1px #2A3035
- Last item: no border

List Item Hover:
- Background: rgba(212, 162, 76, 0.05)

List Item Selected:
- Background: rgba(212, 162, 76, 0.1)
- Border left: 3px #D4A24C
```

### 5.2 Charts & Data Components

**Price Display**:
```
Large Price (Trading View):
- Font: IBM Plex Mono, 32px, bold
- Color: #FFFFFF
- Change indicator: ↑ #1D9B72 or ↓ #A84747
- Percentage: 14px, same color as change
- Background: Optional highlight with 5% opacity

Mini Price:
- Font: IBM Plex Mono, 14px
- Color: #FFFFFF
- Change: 12px, colored

Metric Label:
- Font: Inter, 12px, semibold
- Color: #9FA3A8
- Above price
```

**Progress Bars**:
```
Confidence Score Bar:
- Height: 8px
- Background: #2A3035
- Progress: gradient #D4A24C
- Border radius: 4px

Risk Score Bar:
- Height: 8px
- Background: #2A3035
- Progress: gradient based on level
  - Low: #1D9B72
  - Medium: #C98A21
  - High: #A84747

Percentage Meter:
- Width: 100%
- Numeric value displayed
- Colored bar under text
```

**Sparklines**:
```
Inline Chart:
- Height: 40px
- Color: Single line, #D4A24C
- Background: Optional fill with low opacity
- No axes, minimal styling
- Used in list items, sidebars
```

---

## 6. DASHBOARD STRUCTURE

### 6.1 Overall Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    HEADER (56px)                            │
│  [Logo] [Breadcrumb]     [Search] [Notifications] [Profile] │
└─────────────────────────────────────────────────────────────┘
│                                                             │
│ ┌───────────────┐ ┌───────────────────────────────────────┐ │
│ │               │ │                                       │ │
│ │  SIDEBAR      │ │      MAIN CONTENT AREA               │ │
│ │  (292px)      │ │                                       │ │
│ │               │ │    Market Overview                    │
│ │ • Dashboard   │ │    Council Chamber                    │
│ │ • Council     │ │    Agent Panel                        │
│ │ • Agents      │ │    Voting Panel                       │
│ │ • Portfolio   │ │    Confidence Meter                   │
│ │ • Trade Jrnl  │ │    Portfolio Summary                  │
│ │ • Replay      │ │                                       │
│ │               │ │                                       │
│ │ ─────────────│ │                                       │
│ │ Settings      │ │                                       │
│ │ Docs          │ │                                       │
│ │ Help          │ │                                       │
│ │               │ │                                       │
│ └───────────────┘ └───────────────────────────────────────┘
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Header Layout

```
Height: 56px
Background: #1B1F24
Border bottom: 1px #3A3F45

Left Side (240px):
├─ Council logo (24×24px)
├─ Product name "Council" (16px, semibold)
└─ Divider (1px #3A3F45)

Center (Flexible):
└─ Breadcrumb navigation (14px, secondary text)

Right Side (Align right):
├─ Search bar (200px)
│  └─ Icon + input (32px height)
├─ Notifications bell icon (32px)
│  └─ Badge if unread (8px red dot)
├─ Theme toggle (32px)
└─ Profile dropdown (40px)
   └─ Avatar (32px)
```

### 6.3 Sidebar Navigation

```
Width: 292px
Background: #111315
Border right: 1px #3A3F45
Padding: 24px 0

Logo Section (56px):
├─ Council icon (32×32)
└─ "COUNCIL" text (14px, semibold)

Divider (16px)

Main Navigation (Scrollable):
├─ Dashboard
│  ├─ Home
│  └─ Market Overview
├─ Council
│  ├─ Active Session
│  ├─ Session History
│  └─ Create New
├─ Agents
│  ├─ Performance
│  ├─ Memory Bank
│  └─ Individual Agent
├─ Portfolio
│  ├─ Holdings
│  ├─ Performance
│  └─ Allocation
├─ Trade Journal
│  ├─ Open Trades
│  ├─ Closed Trades
│  └─ Analytics
└─ Council Replay
   ├─ Past Sessions
   └─ Replay Details

Bottom Section (Fixed):
├─ Divider (16px)
├─ Settings
├─ Documentation
├─ Help & Support
└─ Logout
```

### 6.4 Main Content Sections

**Dashboard Home**:
```
Grid: 2 columns
Gap: 24px

Row 1:
├─ Market Overview Card (col 1-2)
│  ├─ Bitcoin price
│  ├─ Ethereum price
│  ├─ Market sentiment
│  └─ 7-day sparklines
└─

Row 2:
├─ Active Sessions (col 1)
│  └─ List of active councils
└─ Portfolio Summary (col 2)
   ├─ Total value
   ├─ Day change
   └─ 30-day chart

Row 3:
├─ Recent Trade Journal (col 1-2)
│  └─ Last 5 trades with status
└─

Row 4:
├─ Top Agent Performance (col 1)
│  └─ Agent rankings
└─ Next Market Event (col 2)
   └─ Scheduled events
```

---

## 7. COUNCIL CHAMBER UI

### 7.1 Council Chamber Layout

```
Height: Full viewport minus header (calc(100vh - 56px))
Background: #111315

┌──────────────────────────────────────────────────────────┐
│ TOP BAR: Session Info & Controls                         │
├──────────────────────────────────────────────────────────┤
│ ┌────────────────┐  ┌────────────────────────────────┐  │
│ │                │  │                                │  │
│ │ DEBATE PANEL   │  │  MARKET DATA DISPLAY           │  │
│ │ (360px)        │  │  (Flexible width)              │  │
│ │                │  │  • Chart (TradingView)         │  │
│ │ • Messages     │  │  • Current Price               │  │
│ │ • Timestamps   │  │  • 24h Change                  │  │
│ │ • Agent names  │  │  • Volume                      │  │
│ │ • Sentiment    │  │  • Volatility                  │  │
│ │                │  │  • Key levels                  │  │
│ │ Scroll as new  │  │                                │  │
│ │ messages come  │  │                                │  │
│ │                │  │                                │  │
│ │ ┌────────────┐ │  │                                │  │
│ │ │ Agent Card │ │  │                                │  │
│ │ │ Agent Card │ │  │                                │  │
│ │ │ Agent Card │ │  │                                │  │
│ │ │ Agent Card │ │  │                                │  │
│ │ │ Agent Card │ │  │                                │  │
│ │ └────────────┘ │  │                                │  │
│ │                │  │                                │  │
│ │ Voting Panel   │  │                                │  │
│ │ [Buttons]      │  │                                │  │
│ │                │  │                                │  │
│ │ Risk Badge     │  │                                │  │
│ │                │  │                                │  │
│ │ Conf. Score    │  │                                │  │
│ │ [0-100]        │  │                                │  │
│ │                │  │                                │  │
│ └────────────────┘  └────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 7.2 Session Info Bar

```
Height: 56px
Background: #1B1F24
Border bottom: 1px #3A3F45
Padding: 0 24px

Content:
├─ Left:
│  ├─ "Council Chamber" (20px, semibold)
│  ├─ Divider (1px #3A3F45)
│  └─ Market: BTC/USD (14px, secondary)
├─ Center: (Timer)
│  ├─ Elapsed: 2:34 (14px, mono)
│  └─ Status: "In Debate Round 2" (12px, secondary)
└─ Right:
   ├─ [Start/Pause/Stop buttons]
   └─ Export Session (ghost button)
```

### 7.3 Debate Message Display

```
Message Container:
├─ Background: #1B1F24
├─ Border left: 3px colored (agent-specific)
├─ Padding: 12px 16px
├─ Border radius: 0 (sharp edges for institutional feel)
├─ Margin: 8px 0

Message Header:
├─ Agent name: 14px, semibold, agent color
├─ Title: "Technical Analysis" (12px, accent gold)
├─ Timestamp: "2:34 PM" (12px, secondary, mono)
└─ Divider: 1px #3A3F45

Message Body:
├─ Content: 14px, regular, white
├─ Key points: bullet list
├─ Data points: highlighted with accent

Message Footer:
├─ Confidence: "92%" (12px, semibold, colored)
├─ Recommendation: "BULLISH" badge
└─ [See Details] link (12px, accent gold)
```

### 7.4 Agent Speaking Indicator

```
During Active Speech:
├─ Agent card: border glow #D4A24C (2px)
├─ Animated pulse (subtle opacity animation)
├─ "SPEAKING NOW" indicator (12px, all caps, accent)
├─ Microphone icon: animated (small animation)
└─ Message typing indicator (if generating)

When Listening:
├─ Agent card: normal border #3A3F45
├─ Opacity: 100%
└─ No special indicator

When Challenged:
├─ Card: border #A84747 (2px)
├─ "CHALLENGED" indicator
└─ Animation: subtle shake
```

---

## 8. AGENT CARDS

### 8.1 Agent Card Layout

```
Width: 100% (in sidebar, typically 320px)
Height: Auto (120px - 200px based on content)
Background: #1B1F24
Border: 1px #3A3F45
Border radius: 4px
Padding: 16px
Margin: 8px 0

Header Row:
├─ Agent Icon (24×24, colored)
├─ Agent Name (14px, semibold, white)
├─ Agent Status Badge (12px, colored badge)
└─ Collapse/Expand Icon (right-aligned)

Content Area:
├─ Role: "Technical Analyst" (12px, secondary)
├─ ─────────────────────────── (divider)
├─ Current State:
│  ├─ Status: "Analyzing" or "Ready" (12px)
│  ├─ Confidence: "87%" (14px, mono, colored)
│  ├─ Last Opinion: "BULLISH" (12px, badge)
│  └─ Processing Time: "1.2s" (11px, secondary)
└─

Footer Row (when speaking):
├─ "→ SPEAKING" (12px, accent gold, animated)
└─ [Interrupt] button (xs size)
```

### 8.2 Agent Color Coding

```
Technical Analyst:
├─ Icon color: #1D9B72 (green)
├─ Border accent: #1D9B72
├─ Primary: "Technical"

News Analyst:
├─ Icon color: #D4A24C (gold)
├─ Border accent: #D4A24C
├─ Primary: "News Sentiment"

Quant Analyst:
├─ Icon color: #6D7175 (gray)
├─ Border accent: #6D7175
├─ Primary: "Quantitative"

Risk Manager:
├─ Icon color: #A84747 (red)
├─ Border accent: #A84747
├─ Primary: "Risk Control"

Execution Agent:
├─ Icon color: #D4A24C (gold, prominent)
├─ Border accent: #D4A24C (thicker: 2px)
├─ Primary: "Final Decision"
```

### 8.3 Expandable Agent Detail View

```
When Clicked/Expanded:
├─ Height: Expands to show full analysis
├─ Background: #2A3035 (elevated)
├─ Padding: 16px

Expanded Content:
├─ Agent Metadata
│  ├─ Role (large, bold)
│  ├─ Performance This Session (%)
│  ├─ Win Rate (historical)
│  └─ Average Confidence
├─ Current Analysis (when available)
│  ├─ Key Findings (3-5 bullet points)
│  ├─ Data Points (with values, colored)
│  ├─ Risk Assessment
│  └─ Recommendation (large badge)
├─ Memory Insights
│  ├─ Similar Past Situations (count)
│  ├─ Historical Accuracy (%)
│  └─ Relevant Past Trades
└─ [Close Details] link
```

---

## 9. VOTING INTERFACE

### 9.1 Voting Panel Layout

```
Position: Bottom of debate panel
Width: 360px
Background: #1B1F24
Border: 1px #3A3F45
Padding: 16px
Border radius: 4px

Header:
├─ "VOTING ROUND" (12px, uppercase, semibold)
├─ "3 of 5 agents voted" (12px, secondary)
└─ Timer: "0:24 remaining" (12px, mono, warning if <10s)

Vote Display (List):
├─ Agent Name (14px)
│  ├─ Vote: "BUY" (badge, colored)
│  ├─ Confidence: 92% (12px, mono, secondary)
│  └─ Timestamp: "2:18 PM" (11px, secondary)
├─ ─────────────────────────── (divider)
├─ [Next agent]
└─ ...

Progress Indicator:
├─ "Consensus Level:" (12px)
├─ Progress bar (showing agreement %)
└─ Visual consensus icon (if 4/5 agree)

Action Area:
├─ For Execution Agent:
│  ├─ [BUY] button (primary, large)
│  ├─ [SELL] button (danger, large)
│  └─ [HOLD] button (secondary, large)
├─
└─ For Other Agents:
   ├─ [BUY] button (md)
   ├─ [SELL] button (md)
   ├─ [HOLD] button (md)
   └─ [ABSTAIN] button (ghost)
```

### 9.2 Vote Result Display

```
After All Votes Collected:

Box:
├─ Background: #2A3035
├─ Border: 2px #D4A24C
├─ Padding: 16px
├─ Border radius: 4px

Content:
├─ "CONSENSUS REACHED" (14px, bold, accent gold)
├─
├─ Vote Breakdown:
│  ├─ BUY: 4 votes (80%) ███████████░░
│  ├─ SELL: 1 vote (20%) ██░░░░░░░░░░
│  └─ HOLD: 0 votes (0%) ░░░░░░░░░░░░
├─
├─ Final Vote: "BUY" (bold, large, #1D9B72)
├─ Confidence Score: "87/100" (large, mono)
└─ [Approve Trade] [Review] buttons
```

### 9.3 Risk Veto Display

```
If Risk Manager VETO:

Alert Box:
├─ Background: rgba(168, 71, 71, 0.15)
├─ Border: 2px #A84747
├─ Padding: 16px
├─ Border radius: 4px

Content:
├─ ⚠️ Icon (20px, danger red)
├─ "VETO: Risk Threshold Exceeded" (14px, bold, red)
├─
├─ Risk Assessment:
│  ├─ Risk Score: 78/100 (too high)
│  ├─ Volatility: High
│  ├─ Exposure: 45% of portfolio
│  ├─ Recommendation: "Reduce position size by 50%"
│  └─
├─ [Adjust & Resubmit] or [Cancel Trade]
```

---

## 10. PORTFOLIO PANEL

### 10.1 Portfolio Summary Layout

```
Position: Right sidebar or expandable panel
Width: 360px (or full-width card on dashboard)
Background: #1B1F24
Border: 1px #3A3F45
Padding: 16px

Header:
├─ "PORTFOLIO" (14px, semibold)
├─ Last updated: "2:42 PM" (11px, secondary)
└─ [Refresh] icon

Portfolio Overview:
├─ Total Value
│  ├─ Amount: "$487,234.50" (24px, mono, bold, white)
│  ├─ Change: "+$12,345.67" (16px, mono, success green)
│  └─ Percentage: "+2.60%" (16px, mono, success green)
├─
├─ 24h Change
│  ├─ Amount: "+$5,234" (14px, mono, colored)
│  └─ Percentage: "+1.09%" (14px, mono, colored)
├─
└─ Allocation Pie Chart (200px, circular)
   ├─ BTC: 45% (#1D9B72)
   ├─ ETH: 30% (#D4A24C)
   ├─ USDT: 15% (#6D7175)
   └─ Other: 10% (#A84747)
```

### 10.2 Holdings List

```
Title: "CURRENT HOLDINGS" (12px, uppercase, semibold)

Table Headers:
├─ Asset (20%)
├─ Amount (20%)
├─ Price (20%)
├─ 24h Change (20%)
└─ Value (20%)

Row (each holding):
├─ Asset
│  ├─ Icon (16×16, colored)
│  ├─ Symbol: "BTC" (14px, bold)
│  └─ Name: "Bitcoin" (12px, secondary)
├─ Amount: "2.5 BTC" (14px, mono)
├─ Price: "$42,350.00" (14px, mono)
├─ Change: "+3.24%" (14px, mono, success green)
│  └─ Icon: ↑
└─ Value: "$105,875.00" (14px, mono, bold)

Row Hover:
├─ Background: rgba(212, 162, 76, 0.05)
├─ Cursor: pointer
└─ [Show Details] option appears

Totals Row:
├─ Border top: 1px #3A3F45
├─ All text: bold
└─ Calculated totals in each column
```

### 10.3 Performance Metrics

```
Section: "PERFORMANCE METRICS"

Metrics Grid (2×2):
├─ Total Return
│  ├─ Value: "+18.45%" (18px, mono, bold, colored)
│  ├─ Label: "Since start" (11px, secondary)
│  └─ Range: "30-day" selector
├─
├─ Sharpe Ratio
│  ├─ Value: "1.87" (18px, mono, bold)
│  ├─ Label: "Risk-adjusted return" (11px, secondary)
│  └─ Benchmark: "vs 1.2 S&P500" (10px, secondary)
├─
├─ Max Drawdown
│  ├─ Value: "-8.3%" (18px, mono, bold, danger)
│  ├─ Label: "Largest decline" (11px, secondary)
│  └─ Date: "Jun 5, 2026" (10px, secondary)
├─
└─ Win Rate
   ├─ Value: "67%" (18px, mono, bold, success)
   ├─ Label: "Profitable trades" (11px, secondary)
   └─ Trades: "21 of 31 trades" (10px, secondary)
```

---

## 11. MOBILE RESPONSIVENESS

### 11.1 Mobile Breakpoints

```
Mobile (320px - 639px):
├─ Single column layout
├─ Sidebar collapses (hamburger menu)
├─ Full-width cards
├─ Stacked sections
├─ Smaller text (14px body → 12px)
├─ Reduced spacing (lg 16px → sm 12px)
└─ Touch-friendly buttons (min 40px)

Tablet (640px - 1023px):
├─ 2-column layout possible
├─ Sidebar toggleable
├─ Responsive grid
├─ Slightly smaller components
└─ Touch optimization maintained

Desktop (1024px+):
├─ Full layout as designed
├─ Sidebar always visible
├─ Multi-column layouts
├─ Hover states active
└─ All features visible
```

### 11.2 Mobile Layout Transformations

**Dashboard (Mobile)**:
```
Header (full-width)
├─ Logo
├─ Hamburger menu
├─ Notifications
└─ Profile

Hamburger Menu (Sidebar):
├─ Overlays content (z-index: 1000)
├─ Overlay backdrop (dark with opacity)
├─ Slide-in from left
├─ Full-height navigation

Main Content (full-width):
├─ Market Overview (card)
├─ Active Sessions (cards, stacked)
├─ Portfolio (cards, stacked)
├─ Trade Journal (cards, stacked)
└─ All 1 column

Footer (sticky):
├─ Primary navigation buttons
├─ BUY / SELL quick actions
└─ Settings / Help links
```

**Council Chamber (Mobile)**:
```
Layout Change:
├─ Debate panel: Full width, 80vh
├─ Chart: Below debate panel, 40vh
├─ Agent cards: Horizontal scroll (carousel)
├─ Voting: Full-width modal overlay
├─ Confidence meter: Inline with voting

Chart Options:
├─ TradingView in responsive mode
├─ Simplified indicators
├─ Single timeframe visible
└─ Zoom/pan via touch gestures

Agent Cards:
├─ Smaller cards (240px width)
├─ Horizontal scroll container
├─ Tap to expand details
└─ Swipe to navigate

Modal:
├─ Full-width overlay
├─ Enters from bottom (slide-up)
├─ Keyboard closes with ESC
└─ Swipe down to close
```

### 11.3 Touch Interactions

```
Button Touch Targets:
├─ Minimum: 40px × 40px
├─ Padding: 12px 16px minimum
└─ Feedback: Active state visible immediately

Swipe Gestures:
├─ Horizontal swipe: Navigate between sections
├─ Vertical swipe up: Open details/modals
├─ Vertical swipe down: Close modals
├─ Long press: Context menu / options

Visual Feedback:
├─ Tap: Slight background color change (200ms)
├─ Press: Held state (opacity/scale)
├─ Release: Return to normal
└─ All feedback: Subtle (no aggressive animations)
```

### 11.4 Responsive Typography

```
Desktop → Mobile Text Scaling:

Display Large:    48px → 28px
Display Medium:   36px → 24px
Display Small:    28px → 20px

Heading 1:        24px → 18px
Heading 2:        20px → 16px
Heading 3:        16px → 14px

Body Large:       16px → 14px
Body Regular:     14px → 13px
Body Small:       12px → 11px

Labels:           12px → 11px (maintain readability)
```

---

## 12. INTERACTION & ANIMATION

### 12.1 Transition Timing

```
Micro-interactions (instant feedback):
├─ Button hover: 100ms
├─ Color change: 100ms
├─ Icon rotation: 150ms
└─ Opacity: 100ms

Medium-interactions (modal opens, panels slide):
├─ Modal: 250ms (ease-out)
├─ Sidebar: 250ms (ease-out)
├─ Panel expand: 300ms (ease-out)
└─ Navigation: 200ms (ease-in-out)

Macro-interactions (page transitions, large animations):
├─ Page fade: 300ms
├─ Chart load: 400ms
├─ Large list render: 300ms per item (staggered)
└─ Scroll behavior: Smooth (browser native)
```

### 12.2 Easing Functions

```
Easing Library (use consistent easing):
├─ Linear: Timing for rotations, progress
├─ Ease-in-out: Most common transitions
├─ Ease-out: Modal opens, panels slide
├─ Ease-in: Page exits, panels collapse
└─ Custom cubic-bezier: For premium feel

Example:
├─ Buttons: cubic-bezier(0.34, 1.56, 0.64, 1) (spring)
├─ Modals: cubic-bezier(0.25, 0.46, 0.45, 0.94) (smooth)
├─ Lists: cubic-bezier(0.25, 0.25, 0.75, 0.75) (linear)
└─ Charts: cubic-bezier(0.17, 0.67, 0.83, 0.67) (ease-in-out)
```

### 12.3 Hover States

```
Button Hover:
├─ Desktop: All interactive elements respond to :hover
├─ Mobile: Removed (no hover on touch)
├─ Color: Transition to lighter/darker shade
├─ Duration: 100ms
└─ Cursor: pointer

Card Hover:
├─ Optional subtle border color change
├─ Background: Optional slight elevation
├─ Duration: 100ms
└─ No movement (maintain layout stability)

Link Hover:
├─ Underline appears: 2px solid, accent color
├─ Color: Brighter gold
├─ Duration: 100ms
└─ Text-decoration-skip-ink: auto
```

### 12.4 Loading States

```
Skeleton Loading:
├─ Placeholder: #2A3035 background
├─ Pulse animation: 1.5s infinite
├─ Opacity: 40% → 80% → 40%
├─ Easing: ease-in-out
└─ Shape: Matches final element

Loading Spinner:
├─ Style: Minimal circle (2px border)
├─ Color: #D4A24C
├─ Size: 24px (md), 16px (sm)
├─ Animation: Rotate 360° over 1s, infinite
└─ Stroke linecap: round

Progress Indicator:
├─ Bar: #D4A24C on #2A3035 background
├─ Height: 3px
├─ Animation: width transition (smooth)
└─ Indeterminate: Animated shift (if duration unknown)
```

---

## 13. DARK MODE & ACCESSIBILITY

### 13.1 Contrast Compliance

All color combinations meet WCAG AA standards:
- Text on background: minimum 4.5:1 ratio
- UI component colors: minimum 3:1 ratio
- Graphics: sufficient contrast for understanding

### 13.2 Accessible Components

```
Forms:
├─ Labels always visible (never placeholder-only)
├─ Error messages associated with inputs
├─ Required indicators (not just color)
├─ Focus outline: 2px solid #D4A24C

Links:
├─ Never rely on color alone
├─ Underline or other indicator
├─ Focus visible in all contexts
├─ aria-current for active page

Images & Icons:
├─ Alt text for all meaningful images
├─ aria-label for icon-only buttons
├─ Sufficient color contrast (icons)
└─ Color + symbol for status (not color alone)

Charts:
├─ Data table alternative provided
├─ Legend easily accessible
├─ Color + pattern/texture differentiation
└─ Keyboard navigation for interactive charts
```

### 13.3 Focus Indicators

```
Focus Visible:
├─ All interactive elements
├─ Outline: 2px solid #D4A24C
├─ Offset: 2px from element
├─ High visibility (no confusion with hover)

Focus Order:
├─ Logical reading order
├─ Tab through sidebar → main content
├─ Modals: Focus trap (cycle within modal)
└─ No keyboard traps

Keyboard Navigation:
├─ Tab: Move to next element
├─ Shift+Tab: Move to previous
├─ Enter: Activate button/link
├─ Space: Toggle checkbox/radio
├─ Arrow keys: Navigate lists/tabs
└─ Escape: Close modals
```

---

## 14. IMPLEMENTATION GUIDELINES

### 14.1 Spacing Consistency

```
Use spacing scale variables:
├─ --spacing-xs: 4px
├─ --spacing-sm: 8px
├─ --spacing-md: 12px
├─ --spacing-lg: 16px
├─ --spacing-xl: 24px
├─ --spacing-xxl: 32px
└─ --spacing-3xl: 48px

Never use arbitrary spacing:
├─ ❌ margin: 15px
├─ ✅ margin: var(--spacing-lg) (16px)
├─ ❌ padding: 18px
├─ ✅ padding: calc(var(--spacing-lg) + 2px)
└─ etc.
```

### 14.2 Color Usage Rules

```
Semantic Colors:
├─ Always use semantic color names
├─ --color-primary-dark: #111315
├─ --color-accent-gold: #D4A24C
├─ --color-status-success: #1D9B72

Never hardcode hex values:
├─ ❌ background-color: #D4A24C
├─ ✅ background-color: var(--color-accent-gold)
└─ Allows easy theme switching

Brand Colors vs Status Colors:
├─ Brand: Primary, Secondary, Accent
├─ Status: Success, Warning, Danger
├─ Use appropriate for context
└─ Never mix concepts
```

### 14.3 Component Sizing

```
Component Sizes:
├─ xs: 24px (compact)
├─ sm: 32px (condensed)
├─ md: 40px (standard)
├─ lg: 48px (spacious)

Never hardcode sizes:
├─ ❌ height: 42px
├─ ✅ height: var(--height-md) or use component
└─ Maintains consistency

Text Sizes (use defined scale only):
├─ Always from type scale
├─ Use semantic class names: `.heading-1`, `.body-large`
├─ Never arbitrary sizes
└─ Responsive via media queries
```

### 14.4 Z-Index Strategy

```
Z-Index Layers:
├─ Base: 0 (default)
├─ Elevated: 10 (cards on hover)
├─ Fixed/Sticky: 100 (header, sidebar)
├─ Dropdown: 200 (dropdowns, popovers)
├─ Modal Backdrop: 500 (semi-transparent overlay)
├─ Modal: 501 (modal itself)
├─ Tooltip: 1000 (always on top)
└─ Never use z-index > 2000

Avoid Stacking Context Conflicts:
├─ Don't nest high z-index elements
├─ Use relative z-index within containers
├─ Document if custom z-index needed
└─ Audit before release
```

---

## STAGE 2 COMPLETE

**Design system documentation generated for all 10 required sections:**

✅ 1. Design system (philosophy, layers, principles)
✅ 2. Color system (core palette, application guide, accessibility)
✅ 3. Typography system (fonts, type scale, weight distribution)
✅ 4. Layout grid (spacing scale, 12-column grid, breakpoints)
✅ 5. Dashboard structure (overall layout, header, sidebar, sections)
✅ 6. Council Chamber UI (debate display, session info, messages)
✅ 7. Agent cards (layout, color coding, expandable details)
✅ 8. Voting interface (voting panel, consensus, risk veto)
✅ 9. Portfolio panel (summary, holdings, performance metrics)
✅ 10. Mobile responsiveness (breakpoints, transformations, touch)

**Additional Sections:**
✅ Interaction & Animation (timing, easing, feedback)
✅ Dark mode & Accessibility (WCAG compliance, keyboard nav)
✅ Implementation guidelines (consistency rules, component sizing)

**Design Aesthetic Achieved:**
✅ Premium institutional feel (Bloomberg Terminal × BlackRock)
✅ Dark theme with strategic gold accents
✅ Minimal ornamentation, data-forward
✅ High information density
✅ Professional, serious tone

**This documentation provides a production-grade design blueprint for Council's UI.**

Ready to proceed to **STAGE 3 — DATABASE SCHEMA**?
