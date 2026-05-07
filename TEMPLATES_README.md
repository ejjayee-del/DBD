# Certificate Template Setup Guide

## Overview
The DBD system uses Microsoft Word (.docx) templates for generating certificates. Templates contain placeholders like `{{recipient_name}}` that get replaced with actual data.

## Current Templates
- `media/templates/Barangay_Clearance.pdf` - PDF template (needs conversion to DOCX)

## Converting PDF to DOCX
1. Open the PDF file in Microsoft Word or Google Docs
2. Save as .docx format
3. Add placeholders using `{{field_name}}` format
4. Save to `media/templates/` directory

## Required Placeholders
For Barangay Clearance, include these placeholders:
- `{{recipient_name}}` - Full name of recipient
- `{{address}}` - Complete address
- `{{civil_status}}` - Single/Married/etc.
- `{{nationality}}` - Citizenship
- `{{years_of_residency}}` - How long they've lived there
- `{{purpose}}` - Reason for certificate
- `{{day}}` - Day of issuance
- `{{month}}` - Month of issuance
- `{{year}}` - Year of issuance
- `{{barangay_name}}` - Barangay name
- `{{municipality}}` - Municipality/City
- `{{official_name}}` - Name of issuing official
- `{{signature}}` - Placeholder for signature image

## Template Registration
After creating DOCX templates, run:
```bash
python manage.py register_templates
```

This will:
1. Scan `media/templates/` for .docx files
2. Extract placeholders from templates
3. Create database entries for each template
4. Set up dynamic forms based on placeholders

## Testing
1. Create at least one .docx template
2. Run template registration
3. Access certificate generation from the admin dashboard
4. Fill out the form and generate a certificate
5. Download the generated .docx file

## Troubleshooting
- Ensure python-docx is installed: `pip install python-docx`
- Templates must be .docx format (not .doc)
- Placeholders must use double curly braces: `{{placeholder}}`
- Signature placeholder should be in a table cell for proper image insertion</content>
<parameter name="filePath">c:\DBD\dbd_project\TEMPLATES_README.md