# Integration Strategy - SharePoint, Teams, MS Word

## Overview

DocSpecSpark integrates with Microsoft 365 ecosystem to provide familiar user experiences while maintaining Git as the authoritative source. This document details the technical integration patterns for SharePoint, Microsoft Teams, and MS Word.

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Interfaces                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ SharePoint   │  │ Teams Bot    │  │ Word Online  │          │
│  │ Document Lib │  │ + Adaptive   │  │ + Desktop    │          │
│  │              │  │   Cards      │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │ Microsoft Graph │
                    │      API        │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐    ┌───────▼──────┐   ┌──────▼──────┐
    │ SharePoint│    │ Teams        │   │ OneDrive    │
    │ Lists +   │    │ Channels +   │   │ (Word files)│
    │ Libraries │    │ Chats        │   │             │
    └─────┬─────┘    └───────┬──────┘   └──────┬──────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │ GitHub Actions  │
                    │ (Sync Engine)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Git Repository  │
                    │ (Source of      │
                    │  Truth)         │
                    └─────────────────┘
```

---

## SharePoint Integration

### 1. Document Library Structure

**Library Configuration**:
```
📁 Published Documents (SharePoint Document Library)
├── 📁 Policies/
│   ├── 📄 Data_Privacy_Policy_v1.0.docx
│   ├── 📄 Information_Security_Policy_v2.1.docx
│   └── 📄 Remote_Work_Policy_v1.5.docx
├── 📁 Handbooks/
│   ├── 📄 Employee_Handbook_v3.2.docx
│   └── 📄 Code_of_Conduct_v2.0.docx
├── 📁 Training/
│   ├── 📄 GDPR_Training_Module_v1.1.docx
│   └── 📄 Security_Awareness_v2.0.docx
└── 📁 _Archive/  (previous versions moved here optionally)
```

**Column Schema**:
```typescript
interface SharePointDocumentMetadata {
  // Default SharePoint columns
  Title: string;
  Modified: Date;
  ModifiedBy: string;
  
  // Custom DocSpecSpark columns
  DocSpecID: string;           // "001-data-privacy-policy"
  DocumentType: string;          // "Policy" | "Handbook" | "Training"
  Version: string;               // "1.0" | "2.1"
  EffectiveDate: Date;
  ExpirationDate: Date;          // For policies with review cycles
  
  ComplianceFrameworks: string[]; // ["GDPR", "SOC2"]
  ComplianceScore: number;        // 0-100
  
  ApprovalStatus: string;         // "Draft" | "Pending" | "Approved" | "Published"
  ApprovedBy: string[];           // ["jane.smith@acme.com", "ceo@acme.com"]
  ApprovalDate: Date;
  
  GitCommitSHA: string;           // Links to Git version
  GitBranch: string;              // "main" for published
  
  Classification: string;         // "Public" | "Internal" | "Confidential"
  Audience: string[];             // ["All Employees", "Managers"]
  
  // Review tracking
  NextReviewDate: Date;
  ReviewCycle: string;            // "Annual" | "Biannual" | "As-Needed"
  ReviewOwner: string;            // "legal-team"
  
  // Searchability
  Keywords: string[];
  RelatedDocuments: string[];     // Links to related policies
}
```

### 2. Microsoft Graph API Integration

**Authentication**:
```javascript
// Using Azure AD App Registration
const credentials = new ClientSecretCredential(
  process.env.AZURE_TENANT_ID,
  process.env.AZURE_CLIENT_ID,
  process.env.AZURE_CLIENT_SECRET
);

const graphClient = Client.initWithMiddleware({
  authProvider: new TokenCredentialAuthenticationProvider(credentials, {
    scopes: [
      'https://graph.microsoft.com/.default',
      'Sites.ReadWrite.All',
      'Files.ReadWrite.All'
    ]
  })
});
```

**Upload Document**:
```javascript
async function publishToSharePoint(
  localFilePath: string,
  metadata: SharePointDocumentMetadata
): Promise<void> {
  const fileBuffer = fs.readFileSync(localFilePath);
  const fileName = `${metadata.Title}_v${metadata.Version}.docx`;
  
  // Step 1: Upload file
  const uploadedFile = await graphClient
    .api(`/sites/${siteId}/drives/${driveId}/root:/${metadata.DocumentType}/${fileName}:/content`)
    .put(fileBuffer);
  
  // Step 2: Set metadata
  await graphClient
    .api(`/sites/${siteId}/lists/${listId}/items/${uploadedFile.id}/fields`)
    .update({
      Title: metadata.Title,
      DocSpecID: metadata.DocSpecID,
      DocumentType: metadata.DocumentType,
      Version: metadata.Version,
      ComplianceFrameworks: metadata.ComplianceFrameworks.join('; '),
      ComplianceScore: metadata.ComplianceScore,
      ApprovalStatus: metadata.ApprovalStatus,
      ApprovedBy: metadata.ApprovedBy.join('; '),
      GitCommitSHA: metadata.GitCommitSHA,
      Classification: metadata.Classification,
      EffectiveDate: metadata.EffectiveDate.toISOString(),
      NextReviewDate: metadata.NextReviewDate.toISOString()
    });
  
  console.log(`✅ Published to SharePoint: ${fileName}`);
}
```

**Download for Editing**:
```javascript
async function downloadFromSharePoint(
  docSpecID: string
): Promise<Buffer> {
  // Find document by custom DocSpecID
  const items = await graphClient
    .api(`/sites/${siteId}/lists/${listId}/items`)
    .filter(`fields/DocSpecID eq '${docSpecID}'`)
    .expand('driveItem')
    .get();
  
  if (items.value.length === 0) {
    throw new Error(`Document not found: ${docSpecID}`);
  }
  
  const driveItemId = items.value[0].driveItem.id;
  
  // Download file content
  const fileStream = await graphClient
    .api(`/drives/${driveId}/items/${driveItemId}/content`)
    .getStream();
  
  return streamToBuffer(fileStream);
}
```

### 3. Bidirectional Sync Strategy

**Scenario 1: Git → SharePoint (Publishing)**
```yaml
# .github/workflows/publish-to-sharepoint.yml
name: Publish Document to SharePoint

on:
  push:
    tags:
      - 'v*'  # Triggers on version tags (v1.0, v2.1, etc.)

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Extract document metadata
        id: metadata
        run: |
          # Parse spec.md and draft.md to extract metadata
          python scripts/extract-metadata.py
      
      - name: Convert Markdown to Word
        run: |
          pandoc .DocSpecSpark/specs/${{ env.DOC_ID }}/draft.md \
            --from markdown \
            --to docx \
            --reference-doc=.DocSpecSpark/templates/company-template.docx \
            --metadata-file=.DocSpecSpark/specs/${{ env.DOC_ID }}/metadata.yaml \
            --output output.docx
      
      - name: Upload to SharePoint
        env:
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
        run: |
          node scripts/sharepoint-upload.js \
            --file output.docx \
            --metadata .DocSpecSpark/specs/${{ env.DOC_ID }}/metadata.yaml
      
      - name: Notify Teams channel
        run: |
          node scripts/teams-notify.js \
            --message "📄 New document published: ${{ env.TITLE }} v${{ env.VERSION }}"
```

**Scenario 2: SharePoint → Git (Editing Published Docs)**
```javascript
// SharePoint Webhook Handler (Azure Function)
module.exports = async function (context, req) {
  const notification = req.body;
  
  // Webhook triggered when document edited in SharePoint
  if (notification.resource === 'driveItem' && notification.changeType === 'updated') {
    const driveItemId = notification.resourceData.id;
    
    // 1. Download updated Word file
    const wordBuffer = await downloadFromSharePoint(driveItemId);
    
    // 2. Convert Word → Markdown (using Pandoc)
    const markdown = await convertWordToMarkdown(wordBuffer);
    
    // 3. Create Git branch for review
    const branchName = `sharepoint-edit-${Date.now()}`;
    await createGitBranch(branchName, markdown);
    
    // 4. Create PR for review
    await createPullRequest({
      branch: branchName,
      title: `[SharePoint Edit] ${documentTitle}`,
      body: `This document was edited directly in SharePoint. Please review changes.`
    });
    
    // 5. Run compliance check on PR
    await triggerComplianceCheck(branchName);
    
    // 6. Notify original author
    await notifyTeams({
      message: `⚠️ ${documentTitle} was edited in SharePoint. Review PR #${prNumber}`
    });
  }
};
```

### 4. SharePoint Custom Actions

**Custom Toolbar Buttons**:
```xml
<!-- SharePoint Framework Extension -->
<CustomAction
  Id="DocSpecReview"
  Title="Ready for Review"
  Description="Submit document for compliance review"
  Location="CommandUI.Ribbon"
  RegistrationType="List"
  RegistrationId="101">  <!-- Document Library -->
  
  <CommandUIExtension>
    <CommandUIDefinitions>
      <CommandUIDefinition Location="Ribbon.Documents.Manage.Controls._children">
        <Button
          Id="Ribbon.Documents.DocSpecReview"
          Command="DocSpec.StartReview"
          Image32by32="/_layouts/15/images/review.png"
          LabelText="Ready for Review"
          TemplateAlias="o1"/>
      </CommandUIDefinition>
    </CommandUIDefinitions>
    
    <CommandUIHandlers>
      <CommandUIHandler
        Command="DocSpec.StartReview"
        CommandAction="javascript:DocSpecSpark.startReview('{ItemId}');" />
    </CommandUIHandlers>
  </CommandUIExtension>
</CustomAction>
```

**JavaScript Handler**:
```javascript
// SharePoint SPFx Extension
class DocSpecSpark {
  static async startReview(itemId: string): Promise<void> {
    // 1. Get document metadata
    const item = await sp.web.lists
      .getByTitle('Published Documents')
      .items.getById(itemId)
      .select('DocSpecID', 'Title', 'FileRef')
      .get();
    
    // 2. Call GitHub API to create review request
    const response = await fetch('https://api.github.com/repos/acme/docspec/dispatches', {
      method: 'POST',
      headers: {
        'Authorization': `token ${githubToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        event_type: 'sharepoint_review_request',
        client_payload: {
          doc_id: item.DocSpecID,
          sharepoint_url: item.FileRef
        }
      })
    });
    
    // 3. Update SharePoint status
    await sp.web.lists
      .getByTitle('Published Documents')
      .items.getById(itemId)
      .update({
        ApprovalStatus: 'Pending Review'
      });
    
    // 4. Show success message
    SP.UI.Notify.addNotification(
      `✅ ${item.Title} submitted for review. You'll receive a Teams notification when complete.`,
      false
    );
  }
}
```

---

## Microsoft Teams Integration

### 1. Teams Bot Architecture

**Bot Framework v4**:
```typescript
// TeamsBot.ts
import { TeamsActivityHandler, CardFactory, TurnContext } from 'botbuilder';

export class DocSpecBot extends TeamsActivityHandler {
  constructor() {
    super();
    
    // Handle message commands
    this.onMessage(async (context, next) => {
      const text = context.activity.text.trim();
      
      if (text.startsWith('/docspec')) {
        await this.handleDocSpecCommand(context, text);
      }
      
      await next();
    });
    
    // Handle adaptive card actions
    this.onInvokeActivity(async (context, next) => {
      if (context.activity.name === 'adaptiveCard/action') {
        await this.handleCardAction(context);
      }
      await next();
    });
  }
  
  private async handleDocSpecCommand(context: TurnContext, command: string): Promise<void> {
    const args = command.split(' ').slice(1);
    
    switch (args[0]) {
      case 'create':
        await this.createDocument(context, args.slice(1).join(' '));
        break;
      
      case 'status':
        await this.getDocumentStatus(context, args[1]);
        break;
      
      case 'approve':
        await this.approveDocument(context, args[1]);
        break;
      
      case 'list':
        await this.listDocuments(context);
        break;
      
      default:
        await context.sendActivity('Usage: `/docspec [create|status|approve|list]`');
    }
  }
  
  private async createDocument(context: TurnContext, title: string): Promise<void> {
    // Send adaptive card wizard
    const card = CardFactory.adaptiveCard({
      type: 'AdaptiveCard',
      version: '1.4',
      body: [
        {
          type: 'TextBlock',
          text: `Create: ${title}`,
          size: 'Large',
          weight: 'Bolder'
        },
        {
          type: 'Input.ChoiceSet',
          id: 'documentType',
          label: 'Document Type',
          choices: [
            { title: 'Policy', value: 'policy' },
            { title: 'Handbook', value: 'handbook' },
            { title: 'Training Material', value: 'training' }
          ]
        },
        {
          type: 'Input.ChoiceSet',
          id: 'frameworks',
          label: 'Compliance Frameworks',
          isMultiSelect: true,
          choices: [
            { title: 'GDPR', value: 'gdpr' },
            { title: 'SOC 2', value: 'soc2' },
            { title: 'HIPAA', value: 'hipaa' },
            { title: 'ISO 9001', value: 'iso9001' },
            { title: 'Labor Law', value: 'labor-law' }
          ]
        }
      ],
      actions: [
        {
          type: 'Action.Submit',
          title: 'Create Document',
          data: { action: 'create_document', title: title }
        }
      ]
    });
    
    await context.sendActivity({ attachments: [card] });
  }
  
  private async handleCardAction(context: TurnContext): Promise<void> {
    const action = context.activity.value;
    
    if (action.action === 'create_document') {
      // Trigger GitHub Action via repository dispatch
      await fetch('https://api.github.com/repos/acme/docspec/dispatches', {
        method: 'POST',
        headers: {
          'Authorization': `token ${process.env.GITHUB_TOKEN}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          event_type: 'create_document',
          client_payload: {
            title: action.title,
            type: action.documentType,
            frameworks: action.frameworks,
            requested_by: context.activity.from.aadObjectId
          }
        })
      });
      
      await context.sendActivity(
        `✅ Creating "${action.title}". I'll notify you when the draft is ready!`
      );
    }
  }
}
```

### 2. Adaptive Cards for Notifications

**Document Ready for Review**:
```json
{
  "type": "AdaptiveCard",
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.4",
  "body": [
  {
      "type": "Container",
      "style": "emphasis",
      "items": [
        {
          "type": "ColumnSet",
          "columns": [
            {
              "type": "Column",
              "width": "auto",
              "items": [
                {
                  "type": "Image",
                  "url": "https://docspec.acme.com/icons/review.png",
                  "size": "Small"
                }
              ]
            },
            {
              "type": "Column",
              "width": "stretch",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "Document Ready for Review",
                  "weight": "Bolder",
                  "size": "Large"
                },
                {
                  "type": "TextBlock",
                  "text": "Data Privacy Policy v1.0",
                  "spacing": "None"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "title": "Author",
          "value": "Sarah Chen (Legal)"
        },
        {
          "title": "Type",
          "value": "Policy"
        },
        {
          "title": "Compliance",
          "value": "✅ GDPR (48/48) | ✅ SOC2 (24/24)"
        },
        {
          "title": "Readability",
          "value": "Grade 11.2 (Target: 12)"
        },
        {
          "title": "Status",
          "value": "Awaiting Legal Approval"
        }
      ]
    },
    {
      "type": "TextBlock",
      "text": "**Key Changes:**\n- Updated data retention from 5 to 7 years\n- Added breach notification timeline (72 hours)\n- Clarified DPO responsibilities",
      "wrap": true
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "Review Document",
      "url": "https://docspec.acme.com/review/001-data-privacy-policy"
    },
    {
      "type": "Action.Submit",
      "title": "✅ Approve",
      "data": {
        "action": "approve",
        "doc_id": "001-data-privacy-policy"
      },
      "style": "positive"
    },
    {
      "type": "Action.Submit",
      "title": "❌ Request Changes",
      "data": {
        "action": "request_changes",
        "doc_id": "001-data-privacy-policy"
      },
      "style": "destructive"
    }
  ]
}
```

### 3. Teams Channel Integration

**Automated Announcements**:
```javascript
// Post to Teams channel when document published
async function announcePublication(document: DocumentMetadata): Promise<void> {
  const webhookUrl = process.env.TEAMS_WEBHOOK_URL;
  
  const message = {
    "@type": "MessageCard",
    "@context": "https://schema.org/extensions",
    "summary": `New Policy Published: ${document.title}`,
    "themeColor": "0076D7",
    "title": `📄 ${document.title} v${document.version} Published`,
    "sections": [
      {
        "activityTitle": `Published by ${document.approvedBy}`,
        "activitySubtitle": new Date().toLocaleDateString(),
        "facts": [
          {
            "name": "Effective Date",
            "value": document.effectiveDate
          },
          {
            "name": "Compliance",
            "value": document.frameworks.join(', ')
          },
          {
            "name": "Audience",
            "value": document.audience
          }
        ],
        "text": document.summary
      }
    ],
    "potentialAction": [
      {
        "@type": "OpenUri",
        "name": "View in SharePoint",
        "targets": [
          {
            "os": "default",
            "uri": document.sharepointUrl
          }
        ]
      },
      {
        "@type": "OpenUri",
        "name": "Download PDF",
        "targets": [
          {
            "os": "default",
            "uri": document.pdfUrl
          }
        ]
      }
    ]
  };
  
  await fetch(webhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(message)
  });
}
```

---

## MS Word Integration

### 1. Pandoc Conversion Pipeline

**Markdown → Word**:
```bash
#!/bin/bash
# scripts/convert-to-word.sh

DOC_ID=$1
VERSION=$2

# Paths
MARKDOWN_FILE=".DocSpecSpark/specs/${DOC_ID}/draft.md"
METADATA_FILE=".DocSpecSpark/specs/${DOC_ID}/metadata.yaml"
TEMPLATE=".DocSpecSpark/templates/company-template.docx"
OUTPUT="output/${DOC_ID}_v${VERSION}.docx"

# Convert with Pandoc
pandoc "$MARKDOWN_FILE" \
  --from markdown+smart+footnotes \
  --to docx \
  --reference-doc="$TEMPLATE" \
  --metadata-file="$METADATA_FILE" \
  --filter pandoc-crossref \
  --lua-filter filters/compliance-citations.lua \
  --output "$OUTPUT" \
  --verbose

echo "✅ Converted to Word: $OUTPUT"
```

**Word → Markdown** (for reverse sync):
```bash
#!/bin/bash
# scripts/convert-from-word.sh

WORD_FILE=$1
OUTPUT_MD=$2

# Convert Word to Markdown
pandoc "$WORD_FILE" \
  --from docx \
  --to markdown+smart \
  --extract-media=media \
  --wrap=none \
  --output "$OUTPUT_MD"

# Clean up Pandoc artifacts
sed -i 's/{#.*}//g' "$OUTPUT_MD"  # Remove auto-generated IDs
sed -i 's/\[\]{.*}//g' "$OUTPUT_MD"  # Remove empty anchors

echo "✅ Converted from Word: $OUTPUT_MD"
```

### 2. Word Template Customization

**Company Template Structure** (`company-template.docx`):
```
Document Properties:
  • Title: {from metadata}
  • Author: {from Git commit}
  • Company: Acme Corporation
  • Version: {from tag}
  • Custom Properties:
    - ComplianceFrameworks
    - DocSpecID
    - GitCommitSHA

Styles (must match Pandoc mapping):
  • Heading 1: Calibri 18pt Bold, Blue (#003366)
  • Heading 2: Calibri 14pt Bold
  • Heading 3: Calibri 12pt Bold
  • Body Text: Calibri 11pt, 1.15 line spacing
  • Quote: Calibri 11pt Italic, Gray background
  • Code: Consolas 10pt, Light gray background
  • Footnote Text: Calibri 9pt (for compliance citations)
  • Table: Bordered, alternating row colors

Header:
  • Company logo (left)
  • Document title (center)
  • Classification watermark (right)

Footer:
  • Version + Date (left)
  • Page numbers (center)
  • "Confidential" + Copyright (right)
```

**Lua Filter for Compliance Citations**:
```lua
-- filters/compliance-citations.lua
-- Converts [GDPR Art. 5] to proper Word footnotes

function Cite(el)
  local citation = pandoc.utils.stringify(el.content)
  
  -- Match patterns like [GDPR Art. 5], [SOC2 CC6.1]
  local framework, reference = citation:match("%[(%w+)%s+(.+)%]")
  
  if framework and reference then
    -- Create footnote with framework details
    local footnote_text = string.format(
      "%s %s: See compliance framework documentation for details.",
      framework, reference
    )
    
    return pandoc.Note({pandoc.Str(footnote_text)})
  end
  
  return el
end
```

### 3. Version Tracking in Word

**Document Properties**:
```xml
<!-- core.xml (embedded in .docx) -->
<coreProperties>
  <dc:title>Data Privacy Policy</dc:title>
  <dc:creator>DocSpecSpark Automation</dc:creator>
  <cp:revision>3</cp:revision>
  <dcterms:created>2026-01-15T10:30:00Z</dcterms:created>
  <dcterms:modified>2026-03-02T14:20:00Z</dcterms:modified>
  
  <!-- Custom properties -->
  <custom:property name="Version" fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="2">
    <vt:lpwstr>1.0</vt:lpwstr>
  </custom:property>
  
  <custom:property name="GitCommitSHA" fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="3">
    <vt:lpwstr>a1b2c3d4e5f6</vt:lpwstr>
  </custom:property>
  
  <custom:property name="ComplianceFrameworks" fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="4">
    <vt:lpwstr>GDPR; SOC2</vt:lpwstr>
  </custom:property>
</coreProperties>
```

**Track Changes Strategy**:
- **Draft Phase**: Track changes **disabled** (AI-generated content, frequent revisions)
- **Review Phase**: Track changes **enabled** (manual human edits only)
- **Published**: Track changes **locked** (read-only, accept all changes)

---

## Sync Conflict Resolution

### Conflict Scenarios

| Scenario | Resolution Strategy |
|----------|---------------------|
| **Git edited, SharePoint edited simultaneously** | Git takes precedence. Create "Conflicted Copy" in SharePoint, notify user. |
| **SharePoint published before Git compliance check** | Block publish. Force compliance check first. |
| **Word → Markdown conversion loses formatting** | Accept loss for unsupported features (e.g., embedded Excel charts). Log warning. |
| **Metadata mismatch (Git vs. SharePoint)** | Git is source of truth. Overwrite SharePoint metadata. |
| **User deletes document from SharePoint** | Warning: "This will archive in Git, not delete." Create archive tag. |

### Locking Mechanism

```javascript
// Prevent simultaneous editing
class DocumentLock {
  private locks: Map<string, LockInfo> = new Map();
  
  async acquireLock(docId: string, userId: string, interface: 'git' | 'sharepoint'): Promise<boolean> {
    if (this.locks.has(docId)) {
      const existingLock = this.locks.get(docId);
      
      if (existingLock.interface !== interface) {
        throw new Error(
          `Document is being edited in ${existingLock.interface} by ${existingLock.userId}. ` +
          `Please wait until they finish.`
        );
      }
    }
    
    this.locks.set(docId, {
      userId,
      interface,
      acquiredAt: new Date(),
      expiresAt: new Date(Date.now() + 30 * 60 * 1000) // 30 min timeout
    });
    
    return true;
  }
  
  async releaseLock(docId: string): Promise<void> {
    this.locks.delete(docId);
  }
}
```

---

## Deployment Checklist

### Azure AD App Registration
- [ ] Create App Registration for Graph API access
- [ ] Grant `Sites.ReadWrite.All`, `Files.ReadWrite.All` permissions
- [ ] Generate Client Secret, store in GitHub Secrets
- [ ] Configure redirect URIs for web app

### SharePoint Site Setup
- [ ] Create "Published Documents" library
- [ ] Add custom columns (DocSpecID, ComplianceFrameworks, etc.)
- [ ] Configure permissions (all employees read, authors edit)
- [ ] Deploy SharePoint Framework extension (custom buttons)
- [ ] Set up webhooks for change notifications

### Teams Bot Deployment
- [ ] Register bot in Azure Bot Service
- [ ] Deploy bot code to Azure App Service
- [ ] Add bot to company Teams tenant
- [ ] Configure messaging endpoint
- [ ] Test adaptive cards in Teams

### GitHub Actions Configuration
- [ ] Add Azure credentials to GitHub Secrets
- [ ] Configure workflows for publish/sync
- [ ] Test pandoc installation in Actions runner
- [ ] Set up scheduled sync job (optional)

---

**Status**: Draft for review
**Next Steps**:
1. Create proof-of-concept SharePoint upload script
2. Build Teams bot prototype
3. Test Pandoc conversion quality
4. Design conflict resolution UX
