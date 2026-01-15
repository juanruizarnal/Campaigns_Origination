"""Airtable schema definitions with exact table and field IDs.

This module centralizes all Airtable table IDs, field IDs, and select options
from the Origination_Campaigns database. Used by agents to read/write data.

Database: Origination_Campaigns
Base ID: appEgNSP0tOLJ9YJ9
Total Tables: 34
Total Fields: 563
"""

# ==============================================================================
# BASE CONFIGURATION
# ==============================================================================

AIRTABLE_BASE_ID = "appEgNSP0tOLJ9YJ9"

# ==============================================================================
# TABLE IDs
# ==============================================================================

TABLES = {
    # Stakeholders (core entities)
    "companies": "tbl47AWmhYAXerbWz",  # Stakeholders_Companies (59 campos)
    "business_units": "tblbBsypFvEnooHlr",  # Stakeholders_Business_Units (38 campos)
    "contacts": "tblfErIdCjpMkXK17",  # Stakeholders_Contacts (33 campos)
    "financials": "tblYiuZOi2VGRXqgA",  # Stakeholders_Companies_Financials (13 campos)
    "company_certificates": "tbl6PZVZasLc0zr9S",  # Company_Certificates (11 campos)
    
    # Origination (campaign management)
    "campaigns": "tbl0B5YGXveYzyADI",  # Origination_Campaigns (23 campos)
    "campaign_targets": "tblblROgAVEcWQ7WQ",  # Campaign_Targets (20 campos)
    "market_context": "tblkE6YhMlxn9XXX5",  # Market_Context (19 campos)
    
    # Configuration (reference tables)
    "config_certificates": "tblQ5HZtmVe2ft9xH",  # Config_Certificates (11 campos)
    "config_activities": "tblcOpprnVmtsMbH4",  # Config_Activities (10 campos)
    "config_countries": "tblC4FxquuxAbf43R",  # Config_Countries (21 campos)
    "config_sectors": "tblo8dIgdxNMJmcx7",  # Config_Sector_And_Activities (14 campos)
    "config_languages": "tblXrAdnl3O16AAyE",  # Config_Languages (6 campos)
    "gics_standard": "tblNjc8JHcC6jT9H9",  # GICS_Standard (8 campos)
    
    # Data Traceability
    "config_sources": "tbl4MEJa6mh1w3EG4",  # Config_Sources (19 campos)
    "source_extractions": "tblXX2Uqa0xQCtHSD",  # Source_Extractions (22 campos)
}


# ==============================================================================
# FIELD IDs - STAKEHOLDERS_COMPANIES
# ==============================================================================

COMPANY_FIELDS = {
    # Basic Info
    "name": "fldqByNrteSCYDyLX",  # Company Name - Text
    "home_url": "fld4CmgZl8zG5AsmF",  # Home URL - Text
    "linkedin_url": "fldDJki7CHM7qzlA9",  # Linkedin URL - URL
    "hq_country": "fldUmivMZQDejw7ZS",  # HQ Country - Link→Config_Countries
    "hq_address": "fldCYJOZjzm1SsSvP",  # HQ Address - Rich Text
    "tax_id": "fldpA5HI4NrqBRt8w",  # Tax ID - Text
    "description": "fldar7tqE2pLCXPaA",  # Description - Rich Text
    "num_employees": "fldRYVqXRaVG1uLT8",  # Num Employees - Number
    "currency": "flde6s7SlSY4sR7xD",  # Currency - Link→Config_Currencies
    
    # Rollup fields
    "company_type": "fldw3mJsSPxdiXCpL",  # Company_Type - Rollup
    "sector": "fldbPI0GGuKcLAFsB",  # Sector - Rollup
    "activities": "flduPFvPTEyGqWSP5",  # Activities - Rollup
    
    # AI Fields
    "gics_sectors_ai": "fldUYmcWYfZxpYGHj",  # GICS Sectors AI
    "gics_industries_ai": "fldZfawXl9lndkhse",  # GICS Industries AI
    
    # Financial Lookups
    "latest_financials_year": "fldnJDBrPshftU0Ip",  # Lookup
    "ebitda": "fldGMWA2OZsE8161S",  # EBITDA - Lookup
    "revenues": "fldMpGZqi1oZhJyKS",  # Revenues - Lookup
    "debt_ebitda": "fldda9mVx6VT8O7A8",  # Debt/EBITDA - Lookup
    
    # Parent Company
    "parent_company": "fldYNfAxCbPYR5cAF",  # Parent Company - Link
    "ultimate_parent": "fldkecnUX1x0YIrHE",  # Ultimate Parent Company - Link
    
    # Relations
    "business_units": "fldTS0EXfmBYkDxkc",  # Business Units - Link
    "contacts": "fldb0auT2qhqTugrc",  # Contacts - Lookup
    "config_certificates": "fldbNeEImVsEkV224",  # Config_Certificates - Link
    "company_certificates": "fldqpfAdKxmxTD1Z4",  # Company_Certificates - Link
    "source_extractions": "fldorLYZxfipbMcJi",  # Source_Extractions - Link
    
    # Traceability
    "source": "fldiTFfi6bEszI0aH",  # Source - MultiSelect
    "pipedrive_id": "fld0OKxtgyr0MLnUq",  # Pipedrive_ID - Text
    "creation_date": "fldf0qiaTEQ0kYZqb",  # Creation Date - CreatedTime
    "update_date": "fldeQA4OE4loBXcRz",  # Update Date - ModifiedTime
    
    # FEI Eligibility Fields (CRITICAL)
    "fei_status": "fldVZcjpAMdtgZAOb",  # FEI_Status - Select
    "fei_criteria_met": "fld38u15eaiiesceW",  # FEI_Criteria_Met - MultiSelect
    "fei_confidence": "fldHza1asHDQKhjqm",  # FEI_Confidence - Percent
    "fei_last_check": "fld8uRn0ClqrWCdKD",  # FEI_Last_Check - Date
    "fei_notes": "fld3vUuTM7UYykrbK",  # FEI_Notes - Long Text
    
    # Other
    "green_checker": "fldIwHzk6bzYr68Wa",  # Green Checker - Checkbox
    "certifications": "fldt2QHbmbcW2vHtW",  # Certifications - Rich Text
    "company_logo": "fldZx8nRJdGqHOKiw",  # Company_Logo - Attachments
}


# ==============================================================================
# FIELD IDs - STAKEHOLDERS_BUSINESS_UNITS
# ==============================================================================

BUSINESS_UNIT_FIELDS = {
    # Basic Info
    "name": "fldrcFl2yl9ZeVbtW",  # Business Unit Name - Text
    "company": "fldwOiPSVOdeRuIIJ",  # Company - Link→Companies
    "business_unit_type": "fldddMbIJ1cyQz6Ut",  # Business Unit Type - Link
    "sector": "fldqhylfII6O9tJnd",  # Sector - Link→Config_Sectors
    "activities": "fld5QXiROXeJw0LVx",  # Activities - Link
    "focus_region": "fldJP1OgYxEgSmanj",  # Focus Region - MultiSelect
    "focus_countries": "fldhg7U43jc6UDNtG",  # Focus Countries - Link
    "additional_info": "fldaHfKYyvw4fc0oO",  # Additional Info - Rich Text
    "record_status": "fldJhTwJFUY576ZdB",  # Record Status - Select
    
    # Contacts
    "business_unit_contacts": "fldLYlKr4gmjDiXeA",  # Business Unit Contacts - Link
    
    # AI Fields
    "gics_ai_summary": "fld2lG6Q14GiQ9NER",  # GICS AI Summary
    "gics_sector": "fldhHSTO6MR2GMVva",  # GICS Sector - AI
    "gics_industry": "fldXbSsvRapRrIwOC",  # GICS Industry - AI
    "gics_subindustry": "fldGOGeS64n2AJfOk",  # GICS Subindustry - AI
    
    # Financial
    "main_currency": "fldQC8u63vi1tBIHC",  # Main Currency - Link
    "ticket_size_min": "fldjJgE49UbJLsW3u",  # Ticket Size Minimum - Number
    "ticket_size_max": "fldmU9ZxftIVReJJr",  # Ticket Size Maximum - Number
    "trust_level": "fldNSLKOxJ5uTcxAJ",  # Trust Level - Percent
    
    # Lookups
    "sector_names": "fld6mjaJNYq5FtDCD",  # Sector_Names - Lookup
    "activities_names": "fld7ayPbKNYYDkHeR",  # Activities_Names - Lookup
    "company_home_url": "fldNByYOWvoUzhAs0",  # Company_Home_URL - Lookup
    "company_linkedin_url": "fldvHaPr8S9eJfNWd",  # Company_Linkedin_URL - Lookup
    
    # Relations
    "config_activities": "flddnKI79EcwFAHv5",  # Config_Activities - Link
    "campaign_targets": "fldKdevQzGADcGlXJ",  # Campaign_Targets - Link
    "source_extractions": "fldeZmDmf1ju2yce5",  # Source_Extractions - Link
    
    # Cooling-off (CRITICAL for campaign targeting)
    "last_outreach_date": "fldLZPFsTnCFpCriq",  # Last_Outreach_Date - Date
    "is_in_cooling_off": "fldD98dTOCUrchFA7",  # Is_In_Cooling_Off - Checkbox
    "revenue_percentage": "fldDZ1uZ3e6UpTlab",  # Revenue_Percentage - Percent (FEI 1.4)
    
    # Timestamps
    "creation_date": "fldrvgDGryCSGVF0U",  # Creation Date - CreatedTime
    "last_update_date": "fldKWDLHVCULsiMdz",  # Last Update Date - ModifiedTime
}


# ==============================================================================
# FIELD IDs - STAKEHOLDERS_CONTACTS
# ==============================================================================

CONTACT_FIELDS = {
    # Basic Info
    "full_name": "fldsvzjNGXEWybta7",  # Full Name - Formula
    "first_name": "fldB8pziOzHr497Qv",  # First Name - Text
    "last_name": "fldf9d2QGtovb61rd",  # Last Name - Text
    "email": "fldEeqx5EiGaDdN6C",  # Email - Email
    "phone_number": "fldSoyxV4vFnFtNSM",  # Phone Number - Phone
    "linkedin_url": "fldOgb4YX2BWw5UFH",  # Linkedin URL - URL
    "key_person": "fldc0Az3Vlf6Rk683",  # Key Person - Select
    "role": "fldV2aedlZ542QL8j",  # Role - Text
    "role_level": "fld6j4LRqyZdzx8b4",  # Role Level - Link
    
    # Relations
    "business_unit": "fldCDSDNQj5rlKpJ8",  # Business Unit - Link
    "company_from_bu": "fldW9uYKs3VBiVQQP",  # Company (from BU) - Lookup
    "contact_type": "fldBJ0IGtlqRTZkHc",  # Contact Type - Link
    "campaign_targets": "flda1jv9LpoCCBfvF",  # Campaign_Targets - Link
    "source_extractions": "fldcEaWE66xggw5ME",  # Source_Extractions - Link
    
    # Other
    "has_responded_before": "fld53Fcjg7Xxgn6QU",  # Has Responded Before - Checkbox
    "description": "fldlYYfhZneAItof8",  # Description - Rich Text
    "contact_languages": "fldmUAt8QbFj4G8UN",  # Contact Languages - Link
    
    # Timestamps
    "creation_date": "fldqxh41eZFPquyvJ",  # Creation Date - CreatedTime
    "update_date": "fldpnrQFZpadHtLW7",  # Update Date - ModifiedTime
}


# ==============================================================================
# FIELD IDs - STAKEHOLDERS_COMPANIES_FINANCIALS
# ==============================================================================

FINANCIALS_FIELDS = {
    "yearly_results_company": "fldGciO4h9XmpPyqk",  # Yearly Results - Company - Formula
    "year": "fldtFQK6pnOGg8NiT",  # Year - Text
    "company": "fld6cJ1oSRiDzDTH6",  # Company - Link
    "company_currency": "fld7Z2RN1DwMQs0cY",  # Company_Currency - Lookup
    "annual_revenues": "fld5B70kDv5mxDnmz",  # Annual_Revenues - Number
    "ebitda": "fldyKupWEWhoBSP1I",  # EBITDA - Number
    "depreciation": "flditYESbQwvfoX52",  # Depreciation - Number
    "impairment": "fldwiAK9N74UqZCRo",  # Impairment - Number
    "ebit": "fld0vQKBrPU37AFe5",  # EBIT - Number
    "fcf": "fld47tJBqJfHlNBMj",  # FCF - Number
    "net_financial_debt": "fldAbKTlEtTlMW2SA",  # Net_Financial_Debt - Number
    "debt_ebitda": "fldjfnA6iVZdwwY4Z",  # Debt/EBITDA - Formula
    "interest_coverage": "fldcQVUZ0tC8CmASj",  # Interest Coverage - Formula
}


# ==============================================================================
# FIELD IDs - ORIGINATION_CAMPAIGNS
# ==============================================================================

CAMPAIGN_FIELDS = {
    # Basic Info
    "campaign_name": "fld4jRij88sR67xZI",  # Campaign_Name - Text
    "description": "flddAgLjzUMofuCCF",  # Description - Rich Text
    "campaign_size": "fldfUzmKxhuowqqTQ",  # Campaign_Size - Select
    "status": "fldV8ZQO4UMGVD6CT",  # Status - Select
    "product_line": "fldGkiulw5ynBfixM",  # Product_Line - MultiSelect
    "priority": "fldaCnwBMBfYp2pOt",  # Priority - Select
    
    # Scheduling
    "scheduled_start_date": "fldsSFYfDKIpuQFnX",  # Scheduled_Start_Date - Date
    "scheduled_end_date": "fldg4320nhYpnopDZ",  # Scheduled_End_Date - Date
    
    # Content
    "campaign_rationale": "fldDBd06rWNFmNmTs",  # Campaign_Rationale - Rich Text
    "email_subject_template_es": "fldPYfxPnhrDuz46M",  # Email_Subject_Template_ES - Text
    "email_subject_template_en": "fldu9QpiLH9P1ZNFz",  # Email_Subject_Template_EN - Text
    "email_body_template_es": "fldz6t0pTdPFbKVtP",  # Email_Body_Template_ES - Rich Text
    "email_body_template_en": "fldhtxiC2uHnjf8W9",  # Email_Body_Template_EN - Rich Text
    
    # Targeting
    "target_ticket_min": "fldFGGz8IPZnhwdlJ",  # Target_Ticket_Min - Number
    "target_ticket_max": "fldYo2bpB8QxjlR0c",  # Target_Ticket_Max - Number
    
    # Relations
    "market_context": "fldB7BZaXkvO4w0Pw",  # Market_Context - Link
    "target_stakeholder_types": "flddGkHXploEHiV75",  # Target_Stakeholder_Types - Link
    "target_sectors": "fldv4yljMidf9Gqw1",  # Target_Sectors - Link
    "target_countries": "fldIwGau3bZwGgIV3",  # Target_Countries - Link
    "owner": "fldrA5YjXct4UFzug",  # Owner - Link
    "campaign_targets": "fldH2x2gIFQrVo3is",  # Campaign_Targets - Link
    
    # Metadata
    "ai_generated": "fldRRtKgjRyO991SH",  # AI_Generated - Checkbox
    "notes": "fldluXqZGlSTzmayH",  # Notes - Rich Text
}


# ==============================================================================
# FIELD IDs - CAMPAIGN_TARGETS
# ==============================================================================

CAMPAIGN_TARGET_FIELDS = {
    # Basic Info
    "target_name": "fldL9UkpndZJl7Jln",  # Target_Name - Text
    "selection_justification": "fldX0Yb8PgjOUSb4q",  # Selection_Justification - Rich Text
    "personalization_context": "fldh23ONjOWUO7yoU",  # Personalization_Context - Rich Text
    
    # Email Content
    "personalized_email_subject": "fldpVFN3JQTNwfsu5",  # Personalized_Email_Subject - Text
    "personalized_email_body": "fldKLrufQL71l5gWP",  # Personalized_Email_Body - Rich Text
    
    # Scoring
    "fit_score": "fldvmDvYtLDDlMaOd",  # Fit_Score - Percent
    "ai_confidence": "fld61Ui1vNKDUk2vP",  # AI_Confidence - Percent
    
    # Status
    "status": "fld0FUxnxP7gftj5B",  # Status - Select
    "sent_date": "fldIepgOOJaadqL2C",  # Sent_Date - DateTime
    "last_interaction_date": "fldAXCBy7kqef9KuT",  # Last_Interaction_Date - DateTime
    "response_summary": "fldKyQCN8priavqD7",  # Response_Summary - Rich Text
    
    # Follow-up
    "follow_up_required": "fldQWBapzlAhAX36E",  # Follow_Up_Required - Checkbox
    "follow_up_notes": "fldoe4pOxUBFZGmTa",  # Follow_Up_Notes - Rich Text
    
    # Override
    "manual_override": "fldbcMfEDJ9Hv3vj9",  # Manual_Override - Checkbox
    "override_notes": "fldn6RaLu0fquzdZl",  # Override_Notes - Rich Text
    
    # Relations
    "campaign": "fldhSdahm4INjtOI1",  # Campaign - Link
    "business_unit": "fldqbbRiQx87Wis8H",  # Business_Unit - Link
    "contact": "fldGP9ex0wKhGNJl6",  # Contact - Link
    "email_activity": "fld90h66w4y3BCfa3",  # Email_Activity - Link
    "source_extractions": "fld6Crde3ts0u2dmF",  # Source_Extractions - Link
}


# ==============================================================================
# FIELD IDs - MARKET_CONTEXT
# ==============================================================================

MARKET_CONTEXT_FIELDS = {
    # Basic Info
    "context_title": "fld6e7BHO9eKWL2m0",  # Context_Title - Text
    "context_type": "fldl4JUDnznJ0jbHP",  # Context_Type - Select
    "source_url": "fldrkFQcovZzh5VER",  # Source_URL - URL
    "source_name": "fldFPpNyjJuiXw0kJ",  # Source_Name - Text
    "publication_date": "fldMqbroY0j8xAcN8",  # Publication_Date - Date
    
    # Content
    "summary": "fld3vxTpETjggyozB",  # Summary - Rich Text
    "key_implications": "fldHLDHrVflPzZEe0",  # Key_Implications - Rich Text
    "notes": "fldtBFfxLnYplhayZ",  # Notes - Rich Text
    
    # Assessment
    "campaign_potential": "fldzf400oERFtimBS",  # Campaign_Potential - Rating (1-5)
    "status": "fldTSwNYaFCYMN2Bt",  # Status - Select
    "relevance_expiry": "flden4dljrQSR5Mld",  # Relevance_Expiry - Date
    "tags": "fld2ASfCovMT5dZu5",  # Tags - MultiSelect
    
    # Relations
    "affected_sectors": "fldbj45oHTaWap8A5",  # Affected_Sectors - Link
    "affected_countries": "fldiGPvAi2vQFrOms",  # Affected_Countries - Link
    "origination_campaigns": "fldnM2RSuR6yRDDDq",  # Origination_Campaigns - Link
    "source_extractions": "fldFDk0VlvfmTZYww",  # Source_Extractions - Link
    
    # Metadata
    "ai_generated": "fldR8yAK9qU6r67lj",  # AI_Generated - Checkbox
    "created_time": "fldZ4TToxiUjHHwcI",  # Created Time - CreatedTime
    "last_modified": "flde1QeRqanFDHBEi",  # Last Modified - ModifiedTime
}


# ==============================================================================
# FIELD IDs - CONFIG_CERTIFICATES
# ==============================================================================

CONFIG_CERTIFICATE_FIELDS = {
    "certificate_name": "fldJf03i94SxYJ1pj",  # Certificate_Name - Text
    "certificate_type": "fldXWCzGxKspCLef7",  # Certificate_Type - MultiSelect
    "certificate_origin": "fldcIvHSqBc77Li5U",  # Certificate_Origin - Select
    "url": "flda8c73vwRLdCXRU",  # URL - URL
    "description": "fldu0aKjrNR630vk0",  # Description - Rich Text
    "fei_eligible": "fldZYcfaOMMS8rUB2",  # FEI_Eligible - Checkbox
    "sustainability_criteria": "fldcRov3Kc2vKYvYt",  # Sustainability_Criteria - Long Text
    "eligible_countries": "fldL6bBDHHq5t5gfT",  # Eligible_Countries - Link
    "valid_countries": "fld70Q2InixSMvqsX",  # Valid_Countries - Link
    "companies": "fldoAs4RlkqwAn3c6",  # Companies - Link
    "company_certificates": "fldidWXxiBuaAbQwN",  # Company_Certificates - Link
}


# ==============================================================================
# FIELD IDs - CONFIG_ACTIVITIES
# ==============================================================================

CONFIG_ACTIVITY_FIELDS = {
    "activity_name": "fldIMTBOcb47ai97r",  # Activity_Name - Text
    "activity_name_en": "fldKkXGqg3iDathN0",  # Activity_Name_EN - Text
    "activity_type": "fldA1z78UTJe5GoMN",  # Activity_Type - MultiSelect
    "activity_sub_type": "fld5QI2PEaYrVYduU",  # Activity_Sub_Type - MultiSelect
    "fei_eligible": "fldFOWaouV3pPpZdR",  # FEI_Eligible - Checkbox
    "is_green_activity": "fld5P5XCmvxGX5zH8",  # Is_Green_Activity - Checkbox
    "eu_taxonomy_category": "fldfymxGFvEhHDCHw",  # EU_Taxonomy_Category - Select
    "description": "fldhhFOJSrkHclbis",  # Description - Rich Text
    "gics_sub_industry": "fldWdshLWcL91BrdW",  # GICS_Sub_Industry - Link
    "business_units": "fldFtj8R3rVwNHrz3",  # Business_Units - Link
}


# ==============================================================================
# FIELD IDs - COMPANY_CERTIFICATES
# ==============================================================================

COMPANY_CERTIFICATE_FIELDS = {
    "certificate_record_name": "fldr8cGkSkDplk8fp",  # Certificate_Record_Name - Text
    "company": "fldOO7EhwQ77fB47d",  # Company - Link
    "certificate_type": "fldsHf8izpzoA3eJ5",  # Certificate_Type - Link
    "certificate_number": "fldKdPOIY2C5VjDDR",  # Certificate_Number - Text
    "issue_date": "fldjeIF31YggnwvXO",  # Issue_Date - Date
    "expiry_date": "fldYpXd9gKtZAfNqj",  # Expiry_Date - Date
    "status": "fldB8RBIO9NKwZTpn",  # Status - Select
    "verification_url": "fldkoVsTlChYhXrr0",  # Verification_URL - URL
    "evidence_attachments": "fldmAA55tQROljUhf",  # Evidence_Attachments - Attachments
    "verification_date": "fldyEsraqrw2tp86m",  # Verification_Date - Date
    "notes": "fldCaeKha6H0jK8mI",  # Notes - Long Text
}


# ==============================================================================
# FIELD IDs - SOURCE_EXTRACTIONS
# ==============================================================================

SOURCE_EXTRACTION_FIELDS = {
    "extraction_name": "fld3vBsvBJDpbpSSZ",  # Extraction_Name - Text
    "source": "fldX4yyOdGBVfd9rg",  # Source - Link
    "extraction_date": "fldRd8WZGH5K9cXd7",  # Extraction_Date - DateTime
    "extracted_by": "fldAKHAXYbftXzO4N",  # Extracted_By - Link
    "target_company": "fld8WxB2IiftVvAGQ",  # Target_Company - Link
    "target_business_unit": "fldQSaOPpKvD6h2LY",  # Target_Business_Unit - Link
    "target_contact": "fldspSyFrhTopYmfn",  # Target_Contact - Link
    "target_market_context": "fldX3e8RGBrFUwIDq",  # Target_Market_Context - Link
    "fields_updated": "fldyTBYmN8HscvcqD",  # Fields_Updated - MultiSelect
    "extraction_url": "flddVZXWx4Mm6FQvY",  # Extraction_URL - URL
    "raw_data_snapshot": "fldMcgLwNya5G7ury",  # Raw_Data_Snapshot - Long Text
    "extraction_status": "fldcwuHScjXCEeIKG",  # Extraction_Status - Select
    "data_quality_score": "fldFvQoIsP6BgKdVX",  # Data_Quality_Score - Rating
    "validated": "fldB8L1MZLM0AC3wg",  # Validated - Checkbox
    "ai_agent_used": "flduxGMW8ZcdHi9yk",  # AI_Agent_Used - Select
    "error_message": "fldiBNLDUMdFoLRmL",  # Error_Message - Long Text
    "processing_time_seconds": "fldgzP4c7KrDZjNkX",  # Processing_Time_Seconds - Number
}


# ==============================================================================
# SELECT OPTIONS - FEI
# ==============================================================================

FEI_STATUS_OPTIONS = [
    "Unknown",
    "Pending_Review",
    "Eligible",
    "Not_Eligible",
    "Partially_Eligible",
    "Expired",
]

FEI_CRITERIA_OPTIONS = [
    "1.1_Cleantech_Prize",
    "1.2_Clean_Energy_Patent",
    "1.3_Eco_Label",
    "1.4_Green_Business_90",
    "1.5_Green_Business_Model",
    "1.6_Environmental_Certificate",
]


# ==============================================================================
# SELECT OPTIONS - CAMPAIGNS
# ==============================================================================

CAMPAIGN_STATUS_OPTIONS = [
    "Draft",
    "Pending_Review",
    "Approved",
    "Scheduled",
    "Active",
    "Paused",
    "Completed",
    "Cancelled",
]

CAMPAIGN_SIZE_OPTIONS = [
    "Massive",
    "Micro-Targeting",
    "Personal",
]

CAMPAIGN_PRIORITY_OPTIONS = [
    "Critical",
    "High",
    "Medium",
    "Low",
]

PRODUCT_LINE_OPTIONS = [
    "Corporate_Debt",
    "Project_Finance",
    "M&A_Advisory",
    "FEI_Guarantee",
    "Refinancing",
    "Bridge_Loan",
]


# ==============================================================================
# SELECT OPTIONS - CAMPAIGN TARGETS
# ==============================================================================

TARGET_STATUS_OPTIONS = [
    "Pending_Review",
    "Approved",
    "Scheduled",
    "Sent",
    "Delivered",
    "Opened",
    "Clicked",
    "Replied",
    "Meeting_Scheduled",
    "Converted",
    "Bounced",
    "Unsubscribed",
    "Rejected",
]


# ==============================================================================
# SELECT OPTIONS - MARKET CONTEXT
# ==============================================================================

CONTEXT_TYPE_OPTIONS = [
    "News_Sectoral",
    "Regulatory_Change",
    "M&A_Movement",
    "Earnings_Report",
    "Funding_Round",
    "Leadership_Change",
    "Market_Trend",
    "Policy_Announcement",
    "Industry_Event",
    "Other",
]

CONTEXT_STATUS_OPTIONS = [
    "New",
    "Analyzed",
    "Campaign_Created",
    "Archived",
    "Discarded",
]

CONTEXT_TAGS_OPTIONS = [
    "Renewables",
    "Infrastructure",
    "Real_Estate",
    "Technology",
    "Healthcare",
    "ESG",
    "FEI_Eligible",
    "Cross_Border",
    "Refinancing",
    "Growth_Capital",
]


# ==============================================================================
# SELECT OPTIONS - CERTIFICATES
# ==============================================================================

CERTIFICATE_TYPE_OPTIONS = [
    "ISO",
    "Eco-label",
    "Prize",
    "PI",
]

CERTIFICATE_STATUS_OPTIONS = [
    "Active",
    "Expired",
    "Pending_Renewal",
    "Revoked",
    "Under_Review",
]


# ==============================================================================
# SELECT OPTIONS - SOURCE EXTRACTIONS
# ==============================================================================

EXTRACTION_STATUS_OPTIONS = [
    "Success",
    "Partial_Success",
    "Failed",
    "Pending_Review",
]

EXTRACTION_TRIGGER_OPTIONS = [
    "Manual",
    "Campaign",
    "Scheduled",
    "AI_Agent",
]

AI_AGENT_OPTIONS = [
    "Buscador_Empresas",
    "Enriquecedor_Datos",
    "Evaluador_FEI",
    "Analizador_Contexto",
    "Selector_Targets",
    "Redactor_Mensajes",
    "None",
]


# ==============================================================================
# SELECT OPTIONS - BUSINESS UNITS
# ==============================================================================

RECORD_STATUS_OPTIONS = [
    "Active",
    "Inactive",
]

FOCUS_REGION_OPTIONS = [
    "AMER",
    "EMEA",
    "APAC",
]

KEY_PERSON_OPTIONS = [
    "Yes",
    "No",
]


# ==============================================================================
# SELECT OPTIONS - ACTIVITIES
# ==============================================================================

EU_TAXONOMY_CATEGORY_OPTIONS = [
    "Climate_Mitigation",
    "Climate_Adaptation",
    "Water_Protection",
    "Circular_Economy",
    "Pollution_Prevention",
    "Biodiversity",
]


# ==============================================================================
# SELECT OPTIONS - COMPANY SOURCE
# ==============================================================================

COMPANY_SOURCE_OPTIONS = [
    "Research",
    "Internal Referral",
    "Web Scraping",
    "Web Form",
    "Partner Referral",
    "LinkedIn Outreach",
    "Event",
    "CRM Migration",
    "Phone Call",
    "Other",
    "Source",
]

