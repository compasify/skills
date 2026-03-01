# Confluence Storage Format Macros

Enterprise-useful macros in Confluence XHTML storage format. Use these when creating/updating content via API.

## Info Panels

```xml
<!-- Info (Blue) -->
<ac:structured-macro ac:name="info">
  <ac:parameter ac:name="title">Information</ac:parameter>
  <ac:rich-text-body><p>Information content</p></ac:rich-text-body>
</ac:structured-macro>

<!-- Note (Yellow) -->
<ac:structured-macro ac:name="note">
  <ac:parameter ac:name="title">Note</ac:parameter>
  <ac:rich-text-body><p>Note content</p></ac:rich-text-body>
</ac:structured-macro>

<!-- Warning (Red) -->
<ac:structured-macro ac:name="warning">
  <ac:parameter ac:name="title">Warning</ac:parameter>
  <ac:rich-text-body><p>Warning content</p></ac:rich-text-body>
</ac:structured-macro>

<!-- Tip (Green) -->
<ac:structured-macro ac:name="tip">
  <ac:parameter ac:name="title">Tip</ac:parameter>
  <ac:rich-text-body><p>Tip content</p></ac:rich-text-body>
</ac:structured-macro>
```

## Table of Contents

```xml
<ac:structured-macro ac:name="toc">
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
  <ac:parameter ac:name="minLevel">1</ac:parameter>
  <ac:parameter ac:name="style">disc</ac:parameter>
</ac:structured-macro>
```

## Expand/Collapse

```xml
<ac:structured-macro ac:name="expand">
  <ac:parameter ac:name="title">Click to view details</ac:parameter>
  <ac:rich-text-body>
    <p>Hidden content here</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

## Status Badges

```xml
<!-- Colors: Green, Yellow, Red, Blue, Grey, Purple -->
<ac:structured-macro ac:name="status">
  <ac:parameter ac:name="colour">Green</ac:parameter>
  <ac:parameter ac:name="title">APPROVED</ac:parameter>
</ac:structured-macro>

<ac:structured-macro ac:name="status">
  <ac:parameter ac:name="colour">Yellow</ac:parameter>
  <ac:parameter ac:name="title">IN REVIEW</ac:parameter>
</ac:structured-macro>

<ac:structured-macro ac:name="status">
  <ac:parameter ac:name="colour">Red</ac:parameter>
  <ac:parameter ac:name="title">BLOCKED</ac:parameter>
</ac:structured-macro>
```

## Code Block

```xml
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">javascript</ac:parameter>
  <ac:parameter ac:name="title">Example Code</ac:parameter>
  <ac:parameter ac:name="linenumbers">true</ac:parameter>
  <ac:plain-text-body><![CDATA[
const express = require('express');
const app = express();
app.listen(3000);
  ]]></ac:plain-text-body>
</ac:structured-macro>
```

**⚠️ Language support:** Confluence DC does NOT support `json` as a language. Use `javascript` for JSON content. Supported languages include: `javascript`, `java`, `python`, `bash`, `sql`, `xml`, `html`, `css`, `typescript`, `csharp`, `php`, `ruby`, `go`, `yaml`.

## Excerpt (Reusable Snippet)

```xml
<ac:structured-macro ac:name="excerpt">
  <ac:parameter ac:name="hidden">false</ac:parameter>
  <ac:rich-text-body>
    <p>This excerpt can be included in other pages.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

## Page Properties (Structured Metadata)

```xml
<ac:structured-macro ac:name="details">
  <ac:rich-text-body>
    <table><tbody>
      <tr><th>Owner</th><td>John Doe</td></tr>
      <tr><th>Status</th><td>
        <ac:structured-macro ac:name="status">
          <ac:parameter ac:name="colour">Green</ac:parameter>
          <ac:parameter ac:name="title">Active</ac:parameter>
        </ac:structured-macro>
      </td></tr>
      <tr><th>Last Review</th><td>2026-02-28</td></tr>
    </tbody></table>
  </ac:rich-text-body>
</ac:structured-macro>
```

## Links

```xml
<!-- Internal page link -->
<ac:link><ri:page ri:content-title="Page Title" ri:space-key="EXAMPLE_SPACE"/></ac:link>

<!-- Link with custom text -->
<ac:link><ri:page ri:content-title="Page Title"/><ac:plain-text-link-body><![CDATA[Custom Link Text]]></ac:plain-text-link-body></ac:link>

<!-- External link (standard HTML works) -->
<a href="https://example.com">External Link</a>
```

## Common Patterns for Enterprise

### Meeting Notes Template
```xml
<ac:structured-macro ac:name="info"><ac:parameter ac:name="title">Meeting Info</ac:parameter>
<ac:rich-text-body><p><strong>Date:</strong> [date]<br/><strong>Attendees:</strong> [names]<br/><strong>Facilitator:</strong> [name]</p></ac:rich-text-body></ac:structured-macro>
<h2>Agenda</h2><ol><li>Item 1</li></ol>
<h2>Discussion</h2><p>[notes]</p>
<h2>Action Items</h2>
<table><thead><tr><th>Action</th><th>Owner</th><th>Deadline</th><th>Status</th></tr></thead>
<tbody><tr><td>[task]</td><td>[name]</td><td>[date]</td><td><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Yellow</ac:parameter><ac:parameter ac:name="title">TODO</ac:parameter></ac:structured-macro></td></tr></tbody></table>
```
