"""Stream type classes for tap-salesforce."""

from __future__ import annotations

import csv
import json
import time
import typing as t
from io import StringIO

import requests
from singer_sdk import typing as th

from tap_salesforce.client import SalesforceStream

PropertiesList = th.PropertiesList
Property = th.Property
ObjectType = th.ObjectType
DateTimeType = th.DateTimeType
StringType = th.StringType
ArrayType = th.ArrayType
BooleanType = th.BooleanType
IntegerType = th.IntegerType
NumberType = th.NumberType

def get_headers(access_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "grant_type": "password",
        "client_id": "",
        "Cookie": "BrowserId=1yJQczWaEe6vlgHTIKdd1A; CookieConsentPolicy=0:1; LSKey-c$CookieConsentPolicy=0:1",
    }
    return headers


class AccountStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_account.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,YearStarted,AccountNumber,AccountSource,AnnualRevenue,BillingAddress,BillingCity,BillingCountry,
                 BillingLatitude,BillingLongitude,BillingPostalCode,BillingState,BillingStreet,BillingGeocodeAccuracy,
                 CleanStatus,Description,DunsNumber,Fax,Industry,Jigsaw,LastActivityDate,LastReferencedDate,LastViewedDate,
                 MasterRecordId,NaicsCode,NaicsDesc,NumberOfEmployees,OperatingHoursId,OwnerId,Ownership,ParentId,Phone,
                 PhotoUrl,Rating,ShippingAddress,ShippingCity,ShippingCountry,ShippingGeocodeAccuracy,ShippingLatitude,
                 ShippingLongitude,ShippingPostalCode,ShippingState,ShippingStreet,Sic,SicDesc,Site,TickerSymbol,Tradestyle,Type,
                 Website,CreatedById,CreatedDate,DandbCompanyId,IsDeleted,JigsawCompanyId,
                 LastModifiedById,LastModifiedDate,SystemModstamp
              """

    entity = "Account"
    name = "accounts"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("YearStarted", StringType),
        Property("AccountNumber", StringType),
        Property("AccountSource", StringType),
        Property("AnnualRevenue", NumberType),
        Property(
            "BillingAddress",
            ObjectType(
                Property("city", StringType),
                Property("country", StringType),
                Property("geocodeAccuracy", StringType),
                Property("latitude", StringType),
                Property("longitude", StringType),
                Property("postalCode", StringType),
                Property("state", StringType),
                Property("street", StringType),
            ),
        ),
        Property("BillingCity", StringType),
        Property("BillingCountry", StringType),
        Property("BillingLatitude", StringType),
        Property("BillingLongitude", StringType),
        Property("BillingPostalCode", StringType),
        Property("BillingState", StringType),
        Property("BillingStreet", StringType),
        Property("BillingGeocodeAccuracy", StringType),
        Property("CleanStatus", StringType),
        Property("Description", StringType),
        Property("DunsNumber", StringType),
        Property("Fax", StringType),
        Property("Industry", StringType),
        Property("Jigsaw", StringType),
        Property("LastActivityDate", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("MasterRecordId", StringType),
        Property("NaicsCode", StringType),
        Property("NaicsDesc", StringType),
        Property("NumberOfEmployees", IntegerType),
        Property("OperatingHoursId", StringType),
        Property("OwnerId", StringType),
        Property("Ownership", StringType),
        Property("ParentId", StringType),
        Property("Phone", StringType),
        Property("PhotoUrl", StringType),
        Property("Rating", StringType),
        Property(
            "ShippingAddress",
            ObjectType(
                Property("city", StringType),
                Property("country", StringType),
                Property("geocodeAccuracy", StringType),
                Property("latitude", StringType),
                Property("longitude", StringType),
                Property("postalCode", StringType),
                Property("state", StringType),
                Property("street", StringType),
            ),
        ),
        Property("ShippingCity", StringType),
        Property("ShippingCountry", StringType),
        Property("ShippingGeocodeAccuracy", StringType),
        Property("ShippingLatitude", StringType),
        Property("ShippingLongitude", StringType),
        Property("ShippingPostalCode", StringType),
        Property("ShippingState", StringType),
        Property("ShippingStreet", StringType),
        Property("Sic", StringType),
        Property("SicDesc", StringType),
        Property("Site", StringType),
        Property("TickerSymbol", StringType),
        Property("Tradestyle", StringType),
        Property("Type", StringType),
        Property("Website", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("DandbCompanyId", StringType),
        Property("IsDeleted", BooleanType),
        Property("JigsawCompanyId", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class ContactStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_contact.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,AccountId,AssistantName,AssistantPhone,Birthdate,CleanStatus,CreatedById,CreatedDate,Department,
                 Description,Email,EmailBouncedDate,EmailBouncedReason,Fax,FirstName,LastName,HomePhone,IndividualId,IsDeleted,
                 IsEmailBounced,Jigsaw,JigsawContactId,LastActivityDate,LastReferencedDate,LastViewedDate,LastCURequestDate,
                 LastCUUpdateDate,LastModifiedById,LastModifiedDate,LeadSource,MailingAddress,MailingCity,MailingCountry,
                 MailingGeocodeAccuracy,MailingLatitude,MailingLongitude,MailingPostalCode,MailingState,MailingStreet,MasterRecordId,
                 MobilePhone,OtherAddress,OtherCity,OtherCountry,OtherGeocodeAccuracy,OtherLatitude,OtherLongitude,OtherPhone,OtherPostalCode,
                 OtherState,OtherStreet,OwnerId,Phone,PhotoUrl,ReportsToId,Salutation,SystemModstamp,Title
              """

    entity = "Contact"
    name = "contacts"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("AccountId", StringType),
        Property("AssistantName", StringType),
        Property("AssistantPhone", StringType),
        Property("Birthdate", StringType),
        Property("CleanStatus", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Department", StringType),
        Property("Description", StringType),
        Property("Email", StringType),
        Property("EmailBouncedDate", StringType),
        Property("EmailBouncedReason", StringType),
        Property("Fax", StringType),
        Property("FirstName", StringType),
        Property("LastName", StringType),
        Property("HomePhone", StringType),
        Property("IndividualId", StringType),
        Property("IsDeleted", BooleanType),
        Property("IsEmailBounced", BooleanType),
        Property("Jigsaw", StringType),
        Property("JigsawContactId", StringType),
        Property("LastActivityDate", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastCURequestDate", StringType),
        Property("LastCUUpdateDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("LeadSource", StringType),
        Property(
            "MailingAddress",
            ObjectType(
                Property("city", StringType),
                Property("country", StringType),
                Property("geocodeAccuracy", StringType),
                Property("latitude", StringType),
                Property("longitude", StringType),
                Property("postalCode", StringType),
                Property("state", StringType),
                Property("street", StringType),
            ),
        ),
        Property("MailingCity", StringType),
        Property("MailingCountry", StringType),
        Property("MailingGeocodeAccuracy", StringType),
        Property("MailingLatitude", StringType),
        Property("MailingLongitude", StringType),
        Property("MailingPostalCode", StringType),
        Property("MailingState", StringType),
        Property("MailingStreet", StringType),
        Property("MasterRecordId", StringType),
        Property("MobilePhone", StringType),
        Property(
            "OtherAddress",
            ObjectType(
                Property("city", StringType),
                Property("country", StringType),
                Property("geocodeAccuracy", StringType),
                Property("latitude", StringType),
                Property("longitude", StringType),
                Property("postalCode", StringType),
                Property("state", StringType),
                Property("street", StringType),
            ),
        ),
        Property("OtherCity", StringType),
        Property("OtherCountry", StringType),
        Property("OtherGeocodeAccuracy", StringType),
        Property("OtherLatitude", StringType),
        Property("OtherLongitude", StringType),
        Property("OtherPhone", StringType),
        Property("OtherPostalCode", StringType),
        Property("OtherState", StringType),
        Property("OtherStreet", StringType),
        Property("OwnerId", StringType),
        Property("Phone", StringType),
        Property("PhotoUrl", StringType),
        Property("ReportsToId", BooleanType),
        Property("Salutation", StringType),
        Property("SystemModstamp", StringType),
        Property("Title", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class CampaignStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_campaign.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,ActualCost,AmountAllOpportunities,AmountWonOpportunities,BudgetedCost,CampaignMemberRecordTypeId,
                 CreatedById,CreatedDate,Description,EndDate,ExpectedResponse,ExpectedRevenue,IsActive,IsDeleted,LastActivityDate,
                 LastReferencedDate,LastViewedDate,LastModifiedById,LastModifiedDate,NumberOfContacts,NumberOfConvertedLeads,
                 NumberOfLeads,NumberOfOpportunities,NumberOfResponses,NumberOfWonOpportunities,NumberSent,OwnerId,ParentId,
                 StartDate,Status,Type,SystemModstamp
              """

    entity = "Campaign"
    name = "campaigns"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("ActualCost", NumberType),
        Property("AmountAllOpportunities", NumberType),
        Property("AmountWonOpportunities", NumberType),
        Property("BudgetedCost", NumberType),
        Property("CampaignMemberRecordTypeId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("EndDate", StringType),
        Property("ExpectedResponse", NumberType),
        Property("ExpectedRevenue", NumberType),
        Property("IsActive", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("LastActivityDate", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", BooleanType),
        Property("NumberOfContacts", IntegerType),
        Property("NumberOfConvertedLeads", IntegerType),
        Property("NumberOfLeads", IntegerType),
        Property("NumberOfOpportunities", IntegerType),
        Property("NumberOfResponses", IntegerType),
        Property("NumberOfWonOpportunities", IntegerType),
        Property("NumberSent", NumberType),
        Property("OwnerId", StringType),
        Property("ParentId", StringType),
        Property("StartDate", StringType),
        Property("Status", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class EntitlementStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_entitlement.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,AccountId,AssetId,BusinessHoursId,CasesPerEntitlement,ContractLineItemId,CreatedById,CreatedDate,EndDate,IsDeleted,
                 IsPerIncident,LastReferencedDate,LastViewedDate,LastModifiedById,LastModifiedDate,LocationId,SvcApptBookingWindowsId,
                 RemainingCases,RemainingWorkOrders,ServiceContractId,SlaProcessId,StartDate,Status,Type,WorkOrdersPerEntitlement,SystemModstamp
              """

    entity = "Entitlement"
    name = "entitlements"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("AccountId", StringType),
        Property("AssetId", StringType),
        Property("BusinessHoursId", StringType),
        Property("CasesPerEntitlement", IntegerType),
        Property("ContractLineItemId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("EndDate", StringType),
        Property("IsDeleted", BooleanType),
        Property("IsPerIncident", BooleanType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("LocationId", StringType),
        Property("SvcApptBookingWindowsId", StringType),
        Property("RemainingCases", IntegerType),
        Property("RemainingWorkOrders", IntegerType),
        Property("ServiceContractId", StringType),
        Property("SlaProcessId", StringType),
        Property("StartDate", StringType),
        Property("Status", StringType),
        Property("Type", StringType),
        Property("WorkOrdersPerEntitlement", IntegerType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class CaseStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_case.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,AccountId,AssetId,Comments,CaseNumber,ClosedDate,ContactEmail,ContactFax,ContactId,ContactMobile,ContactPhone,CreatedById,
                 CreatedDate,Description,IsClosed,IsDeleted,IsEscalated,LastReferencedDate,LastViewedDate,LastModifiedById,
                 LastModifiedDate,MasterRecordId,Origin,OwnerId,ParentId,Priority,Reason,
                 SourceId,Status,Subject,SuppliedCompany,SuppliedEmail,SuppliedName,SuppliedPhone,Type,SystemModstamp
              """

    entity = "Case"
    name = "cases"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("AccountId", StringType),
        Property("AssetId", StringType),
        Property("Comments", StringType),
        Property("CaseNumber", StringType),
        Property("ClosedDate", StringType),
        Property("ContactEmail", StringType),
        Property("ContactFax", StringType),
        Property("ContactId", StringType),
        Property("ContactMobile", StringType),
        Property("ContactPhone", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("IsClosed", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("IsEscalated", BooleanType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("MasterRecordId", StringType),
        Property("Origin", StringType),
        Property("OwnerId", StringType),
        Property("ParentId", StringType),
        Property("Priority", StringType),
        Property("Reason", StringType),
        Property("SourceId", StringType),
        Property("Status", StringType),
        Property("Subject", StringType),
        Property("SuppliedCompany", StringType),
        Property("SuppliedEmail", StringType),
        Property("SuppliedName", StringType),
        Property("SuppliedPhone", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class EmailTemplateStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_emailtemplate.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,ApiVersion,Body,BrandTemplateId,CreatedById,CreatedDate,Description,DeveloperName,Encoding,EnhancedLetterheadId,
                 FolderId,FolderName,HtmlValue,IsActive,IsBuilderContent,LastUsedDate,LastModifiedById,LastModifiedDate,Markup,
                 NamespacePrefix,OwnerId,RelatedEntityType,Subject,TemplateStyle,TemplateType,TimesUsed,UIType,SystemModstamp
              """

    entity = "EmailTemplate"
    name = "email_templates"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("ApiVersion", NumberType),
        Property("Body", StringType),
        Property("BrandTemplateId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("DeveloperName", StringType),
        Property("Encoding", StringType),
        Property("EnhancedLetterheadId", StringType),
        Property("FolderId", StringType),
        Property("FolderName", StringType),
        Property("HtmlValue", StringType),
        Property("IsActive", BooleanType),
        Property("IsBuilderContent", BooleanType),
        Property("LastUsedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("Markup", StringType),
        Property("NamespacePrefix", StringType),
        Property("OwnerId", StringType),
        Property("RelatedEntityType", StringType),
        Property("Subject", StringType),
        Property("TemplateStyle", StringType),
        Property("TemplateType", StringType),
        Property("TimesUsed", IntegerType),
        Property("UiType", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class FolderStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_folder.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,AccessType,CreatedById,CreatedDate,DeveloperName,IsReadonly,LastModifiedById,
                 LastModifiedDate,NamespacePrefix,ParentId,Type,SystemModstamp
              """

    entity = "Folder"
    name = "folders"
    path = "/query?q=SELECT+{}+from+Folder".format(columns)
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("AccessType", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("DeveloperName", StringType),
        Property("IsReadonly", BooleanType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("NamespacePrefix", StringType),
        Property("ParentId", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class GroupStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_group.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,CreatedById,CreatedDate,DeveloperName,DoesIncludeBosses,DoesSendEmailToMembers,
                 Email,LastModifiedById,LastModifiedDate,OwnerId,Type,RelatedId,SystemModstamp
              """

    entity = "Group"
    name = "groups"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("DeveloperName", StringType),
        Property("DoesIncludeBosses", BooleanType),
        Property("DoesSendEmailToMembers", BooleanType),
        Property("Email", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("OwnerId", StringType),
        Property("Type", StringType),
        Property("RelatedId", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class LeadStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_lead.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,Address,AnnualRevenue,City,CleanStatus,Company,CompanyDunsNumber,ConvertedAccountId,ConvertedContactId,
                 ConvertedDate,ConvertedOpportunityId,Country,CreatedById,CreatedDate,DandbCompanyId,Description,
                 Email,EmailBouncedDate,EmailBouncedReason,Fax,FirstName,GeocodeAccuracy,IndividualId,Industry,IsConverted,
                 IsDeleted,IsUnreadByOwner,Jigsaw,JigsawContactId,LastActivityDate,LastName,LastReferencedDate,LastViewedDate,
                 LastModifiedById,LastModifiedDate,Latitude,Longitude,LeadSource,MasterRecordId,MobilePhone,
                 NumberOfEmployees,OwnerId,Phone,PhotoUrl,PostalCode,Rating,Salutation,
                 State,Status,Street,Title,Website,SystemModstamp
              """

    entity = "Lead"
    name = "leads"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property(
            "Address",
            ObjectType(
                Property("city", StringType),
                Property("country", StringType),
                Property("geocodeAccuracy", StringType),
                Property("latitude", StringType),
                Property("longitude", StringType),
                Property("postalCode", StringType),
                Property("state", StringType),
                Property("street", StringType),
            ),
        ),
        Property("AnnualRevenue", NumberType),
        Property("City", StringType),
        Property("CleanStatus", StringType),
        Property("Company", StringType),
        Property("CompanyDunsNumber", StringType),
        Property("ConvertedAccountId", StringType),
        Property("ConvertedContactId", StringType),
        Property("ConvertedDate", StringType),
        Property("ConvertedOpportunityId", StringType),
        Property("Country", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("DandbCompanyId", StringType),
        Property("Description", StringType),
        Property("Email", StringType),
        Property("EmailBouncedDate", StringType),
        Property("EmailBouncedReason", StringType),
        Property("Fax", StringType),
        Property("FirstName", StringType),
        Property("GeocodeAccuracy", StringType),
        Property("IndividualId", StringType),
        Property("Industry", StringType),
        Property("IsConverted", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("IsUnreadByOwner", BooleanType),
        Property("Jigsaw", StringType),
        Property("JigsawContactId", StringType),
        Property("LastActivityDate", StringType),
        Property("LastName", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("Latitude", StringType),
        Property("Longitude", StringType),
        Property("LeadSource", StringType),
        Property("MasterRecordId", StringType),
        Property("MobilePhone", StringType),
        Property("NumberOfEmployees", IntegerType),
        Property("OwnerId", StringType),
        Property("Phone", StringType),
        Property("PhotoUrl", StringType),
        Property("PostalCode", StringType),
        Property("Rating", StringType),
        Property("Salutation", StringType),
        Property("State", StringType),
        Property("Status", StringType),
        Property("Street", StringType),
        Property("Title", StringType),
        Property("Website", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class PeriodStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_period.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,EndDate,FiscalYearSettingsId,FullyQualifiedLabel,IsForecastPeriod,
                 Number,PeriodLabel,QuarterLabel,StartDate,Type,SystemModstamp
              """

    entity = "Period"
    name = "periods"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "StartDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("EndDate", StringType),
        Property("FiscalYearSettingsId", StringType),
        Property("FullyQualifiedLabel", StringType),
        Property("IsForecastPeriod", BooleanType),
        Property("Number", IntegerType),
        Property("PeriodLabel", StringType),
        Property("QuarterLabel", StringType),
        Property("StartDate", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class SolutionStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_solution.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,CreatedById,CreatedDate,IsDeleted,IsHtml,IsPublished,IsPublishedInPublicKb,IsReviewed,
                 LastReferencedDate,LastViewedDate,LastModifiedById,LastModifiedDate,OwnerId,SolutionName,
                 SolutionNote,SolutionNumber,Status,TimesUsed,SystemModstamp
              """

    entity = "Solution"
    name = "solutions"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("IsDeleted", BooleanType),
        Property("IsHtml", BooleanType),
        Property("IsPublished", BooleanType),
        Property("IsPublishedInPublicKb", BooleanType),
        Property("IsReviewed", BooleanType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("OwnerId", StringType),
        Property("SolutionName", StringType),
        Property("SolutionNote", StringType),
        Property("SolutionNumber", StringType),
        Property("Status", StringType),
        Property("TimesUsed", IntegerType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class StaticResourceStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_staticresource.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,Body,BodyLength,CacheControl,ContentType,CreatedById,CreatedDate,Description,
                 LastModifiedById,LastModifiedDate,NamespacePrefix,SystemModstamp
              """

    entity = "StaticResource"
    name = "static_resources"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("Body", StringType),
        Property("BodyLength", IntegerType),
        Property("CacheControl", StringType),
        Property("ContentType", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("NamespacePrefix", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class WebLinkStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_weblink.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,CreatedById,CreatedDate,Description,DisplayType,EncodingKey,HasMenubar,HasScrollbars,HasToolbar,
                 Height,IsProtected,IsResizable,LinkType,LastModifiedById,LastModifiedDate,MasterLabel,NamespacePrefix,OpenType,
                 PageOrSobjectType,Position,RequireRowSelection,ScontrolId,ShowsLocation,ShowsStatus,Url,Width,SystemModstamp
              """

    entity = "WebLink"
    name = "web_links"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("Body", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("DisplayType", StringType),
        Property("EncodingKey", StringType),
        Property("HasMenubar", BooleanType),
        Property("HasScrollbars", BooleanType),
        Property("HasToolbar", BooleanType),
        Property("Height", IntegerType),
        Property("IsProtected", BooleanType),
        Property("IsResizable", BooleanType),
        Property("LinkType", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("MasterLabel", StringType),
        Property("NamespacePrefix", StringType),
        Property("OpenType", StringType),
        Property("PageOrSobjectType", StringType),
        Property("Position", StringType),
        Property("RequireRowSelection", BooleanType),
        Property("ScontrolId", StringType),
        Property("ShowsLocation", BooleanType),
        Property("ShowsStatus", BooleanType),
        Property("Url", StringType),
        Property("Width", IntegerType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class Pricebook2Stream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_pricebook2.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,CreatedById,CreatedDate,Description,IsActive,IsArchived,IsDeleted,IsStandard,
                 LastReferencedDate,LastViewedDate,LastModifiedById,LastModifiedDate,SystemModstamp
              """

    entity = "Pricebook2"
    name = "pricebooks_2"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("IsActive", BooleanType),
        Property("IsArchived", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("IsStandard", BooleanType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class Product2Stream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_product2.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,CreatedById,CreatedDate,Description,DisplayUrl,ExternalDataSourceId,ExternalId,Family,IsActive,IsArchived,
                 IsDeleted,LastReferencedDate,LastViewedDate,LastModifiedById,LastModifiedDate,ProductClass,ProductCode,
                 QuantityUnitOfMeasure,StockKeepingUnit,Type,SystemModstamp
              """

    entity = "Product2"
    name = "products_2"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("DisplayUrl", StringType),
        Property("ExternalDataSourceId", StringType),
        Property("ExternalId", StringType),
        Property("Family", StringType),
        Property("IsActive", BooleanType),
        Property("IsArchived", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("ProductClass", StringType),
        Property("ProductCode", StringType),
        Property("QuantityUnitOfMeasure", StringType),
        Property("StockKeepingUnit", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class PricebookEntryStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_pricebookentry.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,CreatedById,CreatedDate,IsActive,IsArchived,IsDeleted,LastModifiedById,LastModifiedDate,Pricebook2Id,
                 Product2Id,ProductCode,UnitPrice,UseStandardPrice,SystemModstamp
              """

    entity = "PricebookEntry"
    name = "pricebook_entries"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("IsActive", BooleanType),
        Property("IsArchived", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("Pricebook2Id", StringType),
        Property("Product2Id", StringType),
        Property("ProductCode", StringType),
        Property("UnitPrice", NumberType),
        Property("UseStandardPrice", BooleanType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class UserAppInfoStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_userappinfo.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,AppDefinitionId,CreatedById,CreatedDate,FormFactor,IsDeleted,LastModifiedById,LastModifiedDate,UserId,SystemModstamp
              """

    entity = "UserAppInfo"
    name = "user_app_info"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("AppDefinitionId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("FormFactor", StringType),
        Property("IsDeleted", BooleanType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("UserId", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class UserRoleStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_role.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,CaseAccessForAccountOwner,ContactAccessForAccountOwner,DeveloperName,ForecastUserId,LastModifiedById,LastModifiedDate,MayForecastManagerShare,
                 OpportunityAccessForAccountOwner,ParentRoleId,PortalAccountId,PortalAccountOwnerId,PortalType,RollupDescription,SystemModstamp
              """

    entity = "UserRole"
    name = "user_roles"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CaseAccessForAccountOwner", StringType),
        Property("ContactAccessForAccountOwner", StringType),
        Property("DeveloperName", StringType),
        Property("ForecastUserId", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("MayForecastManagerShare", BooleanType),
        Property("OpportunityAccessForAccountOwner", StringType),
        Property("ParentRoleId", StringType),
        Property("PortalAccountId", StringType),
        Property("PortalAccountOwnerId", StringType),
        Property("PortalType", StringType),
        Property("RollupDescription", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class ApexClassStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_apexclass.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,ApiVersion,Body,BodyCrc,CreatedById,CreatedDate,IsValid,LengthWithoutComments,LastModifiedById,LastModifiedDate,
                 NamespacePrefix,Status,SystemModstamp
              """

    entity = "ApexClass"
    name = "apex_classes"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("ApiVersion", NumberType),
        Property("Body", StringType),
        Property("BodyCrc", IntegerType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("IsValid", BooleanType),
        Property("LengthWithoutComments", NumberType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("NamespacePrefix", StringType),
        Property("Status", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class ApexPageStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_apexpage.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,ApiVersion,ControllerKey,ControllerType,CreatedById,CreatedDate,Description,IsAvailableInTouch,
                 IsConfirmationTokenRequired,LastModifiedById,LastModifiedDate,Markup,MasterLabel,NamespacePrefix,SystemModstamp
              """

    entity = "ApexPage"
    name = "apex_pages"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("ApiVersion", NumberType),
        Property("ControllerKey", StringType),
        Property("ControllerType", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("IsAvailableInTouch", BooleanType),
        Property("IsConfirmationTokenRequired", BooleanType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("Markup", StringType),
        Property("MasterLabel", StringType),
        Property("NamespacePrefix", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class ApexTriggerStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_apextrigger.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,ApiVersion,Body,BodyCrc,CreatedById,CreatedDate,IsValid,LengthWithoutComments,LastModifiedById,LastModifiedDate,NamespacePrefix,
                 Status,TableEnumOrId,UsageAfterDelete,UsageAfterInsert,UsageAfterUndelete,UsageAfterUpdate,UsageBeforeDelete,UsageBeforeInsert,
                 UsageBeforeUpdate,UsageIsBulk,SystemModstamp
              """

    entity = "ApexTrigger"
    name = "apex_triggers"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("ApiVersion", NumberType),
        Property("Body", StringType),
        Property("BodyCrc", IntegerType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("IsValid", BooleanType),
        Property("LengthWithoutComments", NumberType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("NamespacePrefix", StringType),
        Property("Status", StringType),
        Property("TableEnumOrId", StringType),
        Property("UsageAfterDelete", BooleanType),
        Property("UsageAfterInsert", BooleanType),
        Property("UsageAfterUndelete", BooleanType),
        Property("UsageAfterUpdate", BooleanType),
        Property("UsageBeforeDelete", BooleanType),
        Property("UsageBeforeInsert", BooleanType),
        Property("UsageBeforeUpdate", BooleanType),
        Property("UsageIsBulk", BooleanType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class CampaignMemberStatusStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_campaignmemberstatus.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,CampaignId,CreatedById,CreatedDate,HasResponded,IsDefault,IsDeleted,Label,LastModifiedById,LastModifiedDate,SortOrder,SystemModstamp
              """

    entity = "CampaignMemberStatus"
    name = "campaign_member_statuses"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("CampaignId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("HasResponded", BooleanType),
        Property("IsDefault", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("Label", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("SortOrder", NumberType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class FiscalYearSettingsStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_fiscalyearsettings.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,Description,EndDate,IsStandardYear,PeriodId,PeriodLabelScheme,PeriodPrefix,QuarterLabelScheme,
                 QuarterPrefix,StartDate,WeekLabelScheme,WeekStartDay,YearType,SystemModstamp
              """

    entity = "FiscalYearSettings"
    name = "fiscal_year_settings"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "StartDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("Description", StringType),
        Property("EndDate", StringType),
        Property("IsStandardYear", BooleanType),
        Property("PeriodId", StringType),
        Property("PeriodLabelScheme", StringType),
        Property("PeriodPrefix", StringType),
        Property("QuarterLabelScheme", StringType),
        Property("QuarterPrefix", StringType),
        Property("StartDate", StringType),
        Property("WeekLabelScheme", StringType),
        Property("WeekStartDay", StringType),
        Property("YearType", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class OpportunityStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_opportunity.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,AccountId,Amount,CampaignId,CloseDate,ContactId,CreatedById,CreatedDate,
                 Description,ExpectedRevenue,Fiscal,FiscalQuarter,FiscalYear,ForecastCategory,ForecastCategoryName,HasOpenActivity,
                 HasOpportunityLineItem,HasOverdueTask,IsClosed,IsDeleted,IsPrivate,IsWon,LastActivityDate,LastAmountChangedHistoryId,
                 LastCloseDateChangedHistoryId,LastReferencedDate,LastStageChangeDate,LastViewedDate,LastModifiedById,LastModifiedDate,LeadSource,
                 NextStep,OwnerId,Pricebook2Id,Probability,PushCount,StageName,TotalOpportunityQuantity,Type,SystemModstamp
              """

    entity = "Opportunity"
    name = "opportunities"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("AccountId", StringType),
        Property("Amount", NumberType),
        Property("CampaignId", StringType),
        Property("CloseDate", StringType),
        Property("ContactId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("ExpectedRevenue", NumberType),
        Property("Fiscal", StringType),
        Property("FiscalQuarter", IntegerType),
        Property("FiscalYear", IntegerType),
        Property("ForecastCategory", StringType),
        Property("ForecastCategoryName", StringType),
        Property("HasOpenActivity", BooleanType),
        Property("HasOpportunityLineItem", BooleanType),
        Property("HasOverdueTask", BooleanType),
        Property("IsClosed", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("IsPrivate", BooleanType),
        Property("IsWon", BooleanType),
        Property("LastActivityDate", StringType),
        Property("LastAmountChangedHistoryId", StringType),
        Property("LastCloseDateChangedHistoryId", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastStageChangeDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("LeadSource", StringType),
        Property("NextStep", StringType),
        Property("OwnerId", StringType),
        Property("Pricebook2Id", StringType),
        Property("Probability", NumberType),
        Property("PushCount", IntegerType),
        Property("StageName", StringType),
        Property("TotalOpportunityQuantity", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class OrganizationStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_organization.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,Division,Street,City,State,PostalCode,Country,Latitude,Longitude,GeocodeAccuracy,Phone,Fax,
                 PrimaryContact,DefaultLocaleSidKey,TimeZoneSidKey,LanguageLocaleKey,ReceivesInfoEmails,
                 ReceivesAdminInfoEmails,PreferencesRequireOpportunityProducts,PreferencesConsentManagementEnabled,
                 PreferencesAutoSelectIndividualOnMerge,PreferencesLightningLoginEnabled,PreferencesOnlyLLPermUserAllowed,
                 FiscalYearStartMonth,UsesStartDateAsFiscalYearName,DefaultAccountAccess,DefaultContactAccess,
                 DefaultOpportunityAccess,DefaultLeadAccess,DefaultCaseAccess,DefaultCalendarAccess,DefaultPricebookAccess,
                 DefaultCampaignAccess,SystemModstamp,ComplianceBccEmail,UiSkin,SignupCountryIsoCode,TrialExpirationDate,
                 NumKnowledgeService,OrganizationType,NamespacePrefix,InstanceName,IsSandbox,WebToCaseDefaultOrigin,
                 MonthlyPageViewsUsed,MonthlyPageViewsEntitlement,IsReadOnly,CreatedDate,CreatedById,LastModifiedDate,
                 PreferencesTransactionSecurityPolicy,LastModifiedById
              """
    columns_remaining = "PreferencesTerminateOldestSession"

    entity = "Organization"
    name = "organizations"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("Division", StringType),
        Property("Street", StringType),
        Property("City", StringType),
        Property("State", StringType),
        Property("PostalCode", StringType),
        Property("Country", StringType),
        Property("Latitude", StringType),
        Property("Longitude", StringType),
        Property("GeocodeAccuracy", StringType),
        Property("Phone", StringType),
        Property("Fax", StringType),
        Property("PrimaryContact", StringType),
        Property("DefaultLocaleSidKey", StringType),
        Property("TimeZoneSidKey", StringType),
        Property("LanguageLocaleKey", StringType),
        Property("ReceivesInfoEmails", BooleanType),
        Property("ReceivesAdminInfoEmails", BooleanType),
        Property("PreferencesRequireOpportunityProducts", BooleanType),
        Property("PreferencesConsentManagementEnabled", BooleanType),
        Property("PreferencesAutoSelectIndividualOnMerge", BooleanType),
        Property("PreferencesLightningLoginEnabled", BooleanType),
        Property("PreferencesOnlyLLPermUserAllowed", BooleanType),
        Property("FiscalYearStartMonth", IntegerType),
        Property("UsesStartDateAsFiscalYearName", BooleanType),
        Property("DefaultAccountAccess", StringType),
        Property("DefaultContactAccess", StringType),
        Property("DefaultOpportunityAccess", StringType),
        Property("DefaultLeadAccess", StringType),
        Property("DefaultCaseAccess", StringType),
        Property("DefaultCalendarAccess", StringType),
        Property("DefaultPricebookAccess", StringType),
        Property("DefaultCampaignAccess", StringType),
        Property("SystemModstamp", StringType),
        Property("ComplianceBccEmail", StringType),
        Property("UiSkin", StringType),
        Property("SignupCountryIsoCode", StringType),
        Property("TrialExpirationDate", StringType),
        Property("NumKnowledgeService", IntegerType),
        Property("OrganizationType", StringType),
        Property("NamespacePrefix", StringType),
        Property("InstanceName", StringType),
        Property("IsSandbox", BooleanType),
        Property("WebToCaseDefaultOrigin", StringType),
        Property("MonthlyPageViewsUsed", IntegerType),
        Property("MonthlyPageViewsEntitlement", IntegerType),
        Property("IsReadOnly", BooleanType),
        Property("CreatedDate", StringType),
        Property("CreatedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("PreferencesTransactionSecurityPolicy", BooleanType),
        Property("PreferencesTerminateOldestSession", BooleanType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class ServiceSetupProvisioningStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_servicesetupprovisioning.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,CreatedById,CreatedDate,IsDeleted,JobName,LastModifiedById,LastModifiedDate,Status,TaskContext,TaskName,SystemModstamp
              """

    entity = "ServiceSetupProvisioning"
    name = "service_setup_provisionings"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("IsDeleted", BooleanType),
        Property("JobName", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("Status", StringType),
        Property("TaskContext", StringType),
        Property("TaskName", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class BusinessHoursStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_businesshours.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,CreatedById,CreatedDate,FridayEndTime,FridayStartTime,IsActive,IsDefault,LastViewedDate,LastModifiedById,LastModifiedDate,MondayEndTime,
                 MondayStartTime,SaturdayEndTime,SaturdayStartTime,SundayEndTime,SundayStartTime,ThursdayEndTime,ThursdayStartTime,TimeZoneSidKey,TuesdayEndTime,
                 TuesdayStartTime,WednesdayEndTime,WednesdayStartTime,SystemModstamp
              """

    entity = "BusinessHours"
    name = "business_hours"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("FridayEndTime", StringType),
        Property("FridayStartTime", StringType),
        Property("IsActive", BooleanType),
        Property("IsDefault", BooleanType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("MondayEndTime", StringType),
        Property("MondayStartTime", StringType),
        Property("SaturdayEndTime", StringType),
        Property("SaturdayStartTime", StringType),
        Property("SundayEndTime", StringType),
        Property("SundayStartTime", StringType),
        Property("ThursdayEndTime", StringType),
        Property("ThursdayStartTime", StringType),
        Property("TimeZoneSidKey", StringType),
        Property("TuesdayEndTime", StringType),
        Property("TuesdayStartTime", StringType),
        Property("WednesdayEndTime", StringType),
        Property("WednesdayStartTime", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class UserStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_user.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Name,AboutMe,AccountId,Address,Alias,BadgeText,BannerPhotoUrl,CallCenterId,City,CommunityNickname,CompanyName,
                 ContactId,Country,CreatedById,CreatedDate,DefaultGroupNotificationFrequency,DelegatedApproverId,Department,DigestFrequency,
                 Division,Email,EmailEncodingKey,EmailPreferencesAutoBcc,EmailPreferencesAutoBccStayInTouch,EmailPreferencesStayInTouchReminder,
                 EmployeeNumber,Extension,Fax,FederationIdentifier,FirstName,ForecastEnabled,FullPhotoUrl,GeocodeAccuracy,IndividualId,IsActive,IsProfilePhotoActive,
                 IsExtIndicatorVisible,JigsawImportLimitOverride,LanguageLocaleKey,LastLoginDate,LastName,LastReferencedDate,LastViewedDate,Latitude,LocaleSidKey,
                 Longitude,LastPasswordChangeDate,LastModifiedById,LastModifiedDate,ManagerId,MediumBannerPhotoUrl,MediumPhotoUrl,MobilePhone,NumberOfFailedLogins,
                 OfflinePdaTrialExpirationDate,OfflineTrialExpirationDate,OutOfOfficeMessage,Phone,PostalCode,ProfileId,ReceivesAdminInfoEmails,ReceivesInfoEmails,
                 SenderEmail,SenderName,Signature,SmallBannerPhotoUrl,SmallPhotoUrl,State,StayInTouchNote,StayInTouchSignature,StayInTouchSubject,Street,TimeZoneSidKey,
                 Title,Username,UserPermissionsCallCenterAutoLogin,UserPermissionsInteractionUser,UserPermissionsJigsawProspectingUser,UserPermissionsKnowledgeUser,
                 UserPermissionsMarketingUser,UserPermissionsOfflineUser,UserPermissionsSFContentUser,UserPermissionsSiteforceContributorUser,
                 UserPermissionsSiteforcePublisherUser,UserPermissionsSupportUser,UserPermissionsWorkDotComUserFeature,UserPreferencesActivityRemindersPopup,
                 UserPreferencesApexPagesDeveloperMode,UserPreferencesCacheDiagnostics,UserPreferencesContentEmailAsAndWhen,UserPreferencesContentNoEmail,
                 UserPreferencesCreateLEXAppsWTShown,UserPreferencesEnableAutoSubForFeeds,UserPreferencesDisableAllFeedsEmail,UserPreferencesDisableBookmarkEmail,
                 UserPreferencesDisableChangeCommentEmail,UserPreferencesDisableEndorsementEmail,UserPreferencesDisableFileShareNotificationsForApi,
                 UserPreferencesDisableFollowersEmail,UserPreferencesDisableLaterCommentEmail,UserPreferencesDisableLikeEmail,UserPreferencesDisableMentionsPostEmail,
                 UserPreferencesDisableProfilePostEmail,UserPreferencesDisableSharePostEmail,UserPreferencesDisCommentAfterLikeEmail,UserPreferencesDisMentionsCommentEmail,
                 UserPreferencesDisableMessageEmail,UserPreferencesDisProfPostCommentEmail,UserPreferencesEventRemindersCheckboxDefault,UserPreferencesExcludeMailAppAttachments,
                 UserPreferencesFavoritesShowTopFavorites,UserPreferencesFavoritesWTShown,UserPreferencesGlobalNavBarWTShown,UserPreferencesGlobalNavGridMenuWTShown,
                 UserPreferencesHasCelebrationBadge,UserPreferencesHasSentWarningEmail,UserPreferencesHasSentWarningEmail238,UserPreferencesHasSentWarningEmail240,
                 UserPreferencesHideBiggerPhotoCallout,UserPreferencesHideChatterOnboardingSplash,UserPreferencesHideCSNDesktopTask,UserPreferencesHideCSNGetChatterMobileTask,
                 UserPreferencesHideEndUserOnboardingAssistantModal,UserPreferencesHideLightningMigrationModal,
                 UserPreferencesHideSecondChatterOnboardingSplash,UserPreferencesHideS1BrowserUI,UserPreferencesHideSfxWelcomeMat,UserPreferencesJigsawListUser,
                 UserPreferencesLightningExperiencePreferred,UserPreferencesNativeEmailClient,UserPreferencesNewLightningReportRunPageEnabled,UserPreferencesPathAssistantCollapsed,
                 UserPreferencesReceiveNoNotificationsAsApprover,UserPreferencesPreviewCustomTheme,UserPreferencesPreviewLightning,UserPreferencesRecordHomeReservedWTShown,
                 UserPreferencesRecordHomeSectionCollapseWTShown,UserPreferencesReverseOpenActivitiesView,UserPreferencesReceiveNotificationsAsDelegatedApprover,
                 UserPreferencesReminderSoundOff,UserPreferencesShowCityToExternalUsers,UserPreferencesShowCityToGuestUsers,UserPreferencesShowCountryToExternalUsers,
                 UserPreferencesShowCountryToGuestUsers,UserPreferencesShowEmailToExternalUsers,UserPreferencesShowEmailToGuestUsers,UserPreferencesShowFaxToExternalUsers,
                 UserPreferencesShowFaxToGuestUsers,UserPreferencesShowForecastingChangeSignals,UserPreferencesShowManagerToExternalUsers,UserPreferencesShowManagerToGuestUsers,
                 UserPreferencesShowMobilePhoneToExternalUsers,UserPreferencesShowMobilePhoneToGuestUsers,UserPreferencesShowPostalCodeToExternalUsers,
                 UserPreferencesShowPostalCodeToGuestUsers,UserPreferencesShowProfilePicToGuestUsers,UserPreferencesShowStateToExternalUsers,
                 UserPreferencesShowStateToGuestUsers,UserPreferencesShowStreetAddressToExternalUsers,UserPreferencesShowStreetAddressToGuestUsers,
                 UserPreferencesShowTitleToExternalUsers,UserPreferencesShowTitleToGuestUsers,UserPreferencesShowTerritoryTimeZoneShifts,
                 UserPreferencesShowWorkPhoneToExternalUsers,UserPreferencesShowWorkPhoneToGuestUsers,UserPreferencesSortFeedByComment,UserPreferencesSRHOverrideActivities,
                 UserPreferencesSuppressEventSFXReminders,UserPreferencesSuppressTaskSFXReminders,UserPreferencesTaskRemindersCheckboxDefault,
                 UserPreferencesUserDebugModePref,UserRoleId,UserType,SystemModstamp
              """

    entity = "User"
    name = "users"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("AboutMe", StringType),
        Property("AccountId", StringType),
        Property(
            "Address",
            ObjectType(
                Property("city", StringType),
                Property("country", StringType),
                Property("geocodeAccuracy", StringType),
                Property("latitude", StringType),
                Property("longitude", StringType),
                Property("postalCode", StringType),
                Property("state", StringType),
                Property("street", StringType),
            ),
        ),
        Property("Alias", StringType),
        Property("BadgeText", StringType),
        Property("BannerPhotoUrl", StringType),
        Property("CallCenterId", StringType),
        Property("City", StringType),
        Property("CommunityNickname", StringType),
        Property("CompanyName", StringType),
        Property("ContactId", StringType),
        Property("Country", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("DefaultGroupNotificationFrequency", StringType),
        Property("DelegatedApproverId", StringType),
        Property("Department", StringType),
        Property("DigestFrequency", StringType),
        Property("Division", StringType),
        Property("Email", StringType),
        Property("EmailEncodingKey", StringType),
        Property("EmailPreferencesAutoBcc", BooleanType),
        Property("EmailPreferencesAutoBccStayInTouch", BooleanType),
        Property("EmailPreferencesStayInTouchReminder", BooleanType),
        Property("EmployeeNumber", StringType),
        Property("Extension", StringType),
        Property("Fax", StringType),
        Property("FederationIdentifier", StringType),
        Property("FirstName", StringType),
        Property("ForecastEnabled", BooleanType),
        Property("FullPhotoUrl", StringType),
        Property("GeocodeAccuracy", StringType),
        Property("IndividualId", StringType),
        Property("IsActive", BooleanType),
        Property("IsProfilePhotoActive", BooleanType),
        Property("IsExtIndicatorVisible", BooleanType),
        Property("JigsawImportLimitOverride", IntegerType),
        Property("LanguageLocaleKey", StringType),
        Property("LastLoginDate", StringType),
        Property("LastName", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("Latitude", StringType),
        Property("LocaleSidKey", StringType),
        Property("Longitude", StringType),
        Property("LastPasswordChangeDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("ManagerId", StringType),
        Property("MediumBannerPhotoUrl", StringType),
        Property("MediumPhotoUrl", StringType),
        Property("MobilePhone", StringType),
        Property("NumberOfFailedLogins", IntegerType),
        Property("OfflinePdaTrialExpirationDate", StringType),
        Property("OfflineTrialExpirationDate", StringType),
        Property("OutOfOfficeMessage", StringType),
        Property("Phone", StringType),
        Property("PostalCode", StringType),
        Property("ProfileId", StringType),
        Property("ReceivesAdminInfoEmails", BooleanType),
        Property("ReceivesInfoEmails", BooleanType),
        Property("SenderEmail", StringType),
        Property("SenderName", StringType),
        Property("Signature", StringType),
        Property("SmallBannerPhotoUrl", StringType),
        Property("SmallPhotoUrl", StringType),
        Property("State", StringType),
        Property("StayInTouchNote", StringType),
        Property("StayInTouchSignature", StringType),
        Property("StayInTouchSubject", StringType),
        Property("Street", StringType),
        Property("TimeZoneSidKey", StringType),
        Property("Title", StringType),
        Property("Username", StringType),
        Property("UserPermissionsCallCenterAutoLogin", BooleanType),
        Property("UserPermissionsInteractionUser", BooleanType),
        Property("UserPermissionsJigsawProspectingUser", BooleanType),
        Property("UserPermissionsKnowledgeUser", BooleanType),
        Property("UserPermissionsMarketingUser", BooleanType),
        Property("UserPermissionsOfflineUser", BooleanType),
        Property("UserPermissionsSFContentUser", BooleanType),
        Property("UserPermissionsSiteforceContributorUser", BooleanType),
        Property("UserPermissionsSiteforcePublisherUser", BooleanType),
        Property("UserPermissionsSupportUser", BooleanType),
        Property("UserPermissionsWorkDotComUserFeature", BooleanType),
        Property("UserPreferencesActivityRemindersPopup", BooleanType),
        Property("UserPreferencesApexPagesDeveloperMode", BooleanType),
        Property("UserPreferencesCacheDiagnostics", BooleanType),
        Property("UserPreferencesContentEmailAsAndWhen", BooleanType),
        Property("UserPreferencesContentNoEmail", BooleanType),
        Property("UserPreferencesCreateLEXAppsWTShown", BooleanType),
        Property("UserPreferencesEnableAutoSubForFeeds", BooleanType),
        Property("UserPreferencesDisableAllFeedsEmail", BooleanType),
        Property("UserPreferencesDisableBookmarkEmail", BooleanType),
        Property("UserPreferencesDisableChangeCommentEmail", BooleanType),
        Property("UserPreferencesDisableEndorsementEmail", BooleanType),
        Property("UserPreferencesDisableFileShareNotificationsForApi", BooleanType),
        Property("UserPreferencesDisableFollowersEmail", BooleanType),
        Property("UserPreferencesDisableLaterCommentEmail", BooleanType),
        Property("UserPreferencesDisableLikeEmail", BooleanType),
        Property("UserPreferencesDisableMentionsPostEmail", BooleanType),
        Property("UserPreferencesDisableProfilePostEmail", BooleanType),
        Property("UserPreferencesDisableSharePostEmail", BooleanType),
        Property("UserPreferencesDisCommentAfterLikeEmail", BooleanType),
        Property("UserPreferencesDisMentionsCommentEmail", BooleanType),
        Property("UserPreferencesDisableMessageEmail", BooleanType),
        Property("UserPreferencesDisProfPostCommentEmail", BooleanType),
        Property("UserPreferencesEventRemindersCheckboxDefault", BooleanType),
        Property("UserPreferencesExcludeMailAppAttachments", BooleanType),
        Property("UserPreferencesFavoritesShowTopFavorites", BooleanType),
        Property("UserPreferencesFavoritesWTShown", BooleanType),
        Property("UserPreferencesGlobalNavBarWTShown", BooleanType),
        Property("UserPreferencesGlobalNavGridMenuWTShown", BooleanType),
        Property("UserPreferencesHasCelebrationBadge", BooleanType),
        Property("UserPreferencesHasSentWarningEmail", BooleanType),
        Property("UserPreferencesHasSentWarningEmail238", BooleanType),
        Property("UserPreferencesHasSentWarningEmail240", BooleanType),
        Property("UserPreferencesHideBiggerPhotoCallout", BooleanType),
        Property("UserPreferencesHideChatterOnboardingSplash", BooleanType),
        Property("UserPreferencesHideCSNDesktopTask", BooleanType),
        Property("UserPreferencesHideCSNGetChatterMobileTask", BooleanType),
        Property("UserPreferencesHideEndUserOnboardingAssistantModal", BooleanType),
        Property("UserPreferencesHideLightningMigrationModal", BooleanType),
        Property("UserPreferencesHideSecondChatterOnboardingSplash", BooleanType),
        Property("UserPreferencesHideS1BrowserUI", BooleanType),
        Property("UserPreferencesHideSfxWelcomeMat", BooleanType),
        Property("UserPreferencesJigsawListUser", BooleanType),
        Property("UserPreferencesLightningExperiencePreferred", BooleanType),
        Property("UserPreferencesNativeEmailClient", BooleanType),
        Property("UserPreferencesNewLightningReportRunPageEnabled", BooleanType),
        Property("UserPreferencesPathAssistantCollapsed", BooleanType),
        Property("UserPreferencesPreviewCustomTheme", BooleanType),
        Property("UserPreferencesPreviewLightning", BooleanType),
        Property("UserPreferencesRecordHomeReservedWTShown", BooleanType),
        Property("UserPreferencesRecordHomeSectionCollapseWTShown", BooleanType),
        Property("UserPreferencesReceiveNoNotificationsAsApprover", BooleanType),
        Property("UserPreferencesReceiveNotificationsAsDelegatedApprover", BooleanType),
        Property("UserPreferencesReminderSoundOff", BooleanType),
        Property("UserPreferencesReverseOpenActivitiesView", BooleanType),
        Property("UserPreferencesShowCityToExternalUsers", BooleanType),
        Property("UserPreferencesShowCityToGuestUsers", BooleanType),
        Property("UserPreferencesShowCountryToExternalUsers", BooleanType),
        Property("UserPreferencesShowCountryToGuestUsers", BooleanType),
        Property("UserPreferencesShowEmailToExternalUsers", BooleanType),
        Property("UserPreferencesShowEmailToGuestUsers", BooleanType),
        Property("UserPreferencesShowFaxToExternalUsers", BooleanType),
        Property("UserPreferencesShowFaxToGuestUsers", BooleanType),
        Property("UserPreferencesShowForecastingChangeSignals", BooleanType),
        Property("UserPreferencesShowManagerToExternalUsers", BooleanType),
        Property("UserPreferencesShowManagerToGuestUsers", BooleanType),
        Property("UserPreferencesShowMobilePhoneToExternalUsers", BooleanType),
        Property("UserPreferencesShowMobilePhoneToGuestUsers", BooleanType),
        Property("UserPreferencesShowPostalCodeToExternalUsers", BooleanType),
        Property("UserPreferencesShowPostalCodeToGuestUsers", BooleanType),
        Property("UserPreferencesShowProfilePicToGuestUsers", BooleanType),
        Property("UserPreferencesShowStateToExternalUsers", BooleanType),
        Property("UserPreferencesShowStateToGuestUsers", BooleanType),
        Property("UserPreferencesShowStreetAddressToExternalUsers", BooleanType),
        Property("UserPreferencesShowStreetAddressToGuestUsers", BooleanType),
        Property("UserPreferencesShowTitleToExternalUsers", BooleanType),
        Property("UserPreferencesShowTitleToGuestUsers", BooleanType),
        Property("UserPreferencesShowTerritoryTimeZoneShifts", BooleanType),
        Property("UserPreferencesShowWorkPhoneToExternalUsers", BooleanType),
        Property("UserPreferencesShowWorkPhoneToGuestUsers", BooleanType),
        Property("UserPreferencesSortFeedByComment", BooleanType),
        Property("UserPreferencesSRHOverrideActivities", BooleanType),
        Property("UserPreferencesSuppressEventSFXReminders", BooleanType),
        Property("UserPreferencesSuppressTaskSFXReminders", BooleanType),
        Property("UserPreferencesTaskRemindersCheckboxDefault", BooleanType),
        Property("UserPreferencesUserDebugModePref", BooleanType),
        Property("UserRoleId", StringType),
        Property("UserType", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class ProfileStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_businesshours.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id,Description,LastReferencedDate,PermissionsEmailSingle,PermissionsEmailMass,PermissionsEditTask,PermissionsEditEvent,
                 PermissionsExportReport,PermissionsImportPersonal,PermissionsDataExport,PermissionsManageUsers,PermissionsEditPublicFilters,
                 PermissionsEditPublicTemplates,PermissionsModifyAllData,PermissionsEditBillingInfo,PermissionsManageCases,
                 PermissionsMassInlineEdit,PermissionsEditKnowledge,PermissionsManageKnowledge,PermissionsManageSolutions,
                 PermissionsCustomizeApplication,PermissionsEditReadonlyFields,PermissionsRunReports,PermissionsViewSetup,
                 PermissionsTransferAnyEntity,PermissionsNewReportBuilder,PermissionsActivateContract,PermissionsActivateOrder,
                 PermissionsImportLeads,PermissionsManageLeads,PermissionsTransferAnyLead,PermissionsViewAllData,PermissionsEditPublicDocuments,
                 PermissionsViewEncryptedData,PermissionsEditBrandTemplates,PermissionsEditHtmlTemplates,PermissionsChatterInternalUser,
                 PermissionsManageEncryptionKeys,PermissionsDeleteActivatedContract,PermissionsChatterInviteExternalUsers,
                 PermissionsSendSitRequests,PermissionsApiUserOnly,PermissionsManageRemoteAccess,PermissionsCanUseNewDashboardBuilder,
                 PermissionsManageCategories,PermissionsConvertLeads,PermissionsPasswordNeverExpires,PermissionsUseTeamReassignWizards,
                 PermissionsEditActivatedOrders,PermissionsInstallMultiforce,PermissionsPublishMultiforce,PermissionsChatterOwnGroups,
                 PermissionsEditOppLineItemUnitPrice,PermissionsCreateMultiforce,PermissionsBulkApiHardDelete,PermissionsSolutionImport,
                 PermissionsManageCallCenters,PermissionsManageSynonyms,PermissionsViewContent,PermissionsManageEmailClientConfig,
                 PermissionsEnableNotifications,PermissionsManageDataIntegrations,PermissionsDistributeFromPersWksp,PermissionsViewDataCategories,
                 PermissionsManageDataCategories,PermissionsAuthorApex,PermissionsManageMobile,PermissionsApiEnabled,PermissionsManageCustomReportTypes,
                 PermissionsEditCaseComments,PermissionsTransferAnyCase,PermissionsContentAdministrator,PermissionsCreateWorkspaces,
                 PermissionsManageContentPermissions,PermissionsManageContentProperties,PermissionsManageContentTypes,PermissionsManageExchangeConfig,
                 PermissionsManageAnalyticSnapshots,PermissionsScheduleReports,PermissionsManageBusinessHourHolidays,PermissionsManageEntitlements,
                 PermissionsManageDynamicDashboards,PermissionsCustomSidebarOnAllPages,PermissionsManageInteraction,PermissionsViewMyTeamsDashboards,
                 PermissionsModerateChatter,PermissionsResetPasswords,PermissionsFlowUFLRequired,PermissionsCanInsertFeedSystemFields,
                 PermissionsActivitiesAccess,PermissionsManageKnowledgeImportExport,PermissionsEmailTemplateManagement,PermissionsEmailAdministration,
                 PermissionsManageChatterMessages,PermissionsAllowEmailIC,PermissionsChatterFileLink,PermissionsForceTwoFactor,
                 PermissionsViewEventLogFiles,PermissionsManageNetworks,PermissionsManageAuthProviders,PermissionsRunFlow,
                 PermissionsCreateCustomizeDashboards,PermissionsCreateDashboardFolders,PermissionsViewPublicDashboards,
                 PermissionsManageDashbdsInPubFolders,PermissionsCreateCustomizeReports,PermissionsCreateReportFolders,PermissionsViewPublicReports,
                 PermissionsManageReportsInPubFolders,PermissionsEditMyDashboards,PermissionsEditMyReports,PermissionsViewAllUsers,
                 PermissionsAllowUniversalSearch,PermissionsConnectOrgToEnvironmentHub,PermissionsWorkCalibrationUser,PermissionsCreateCustomizeFilters,
                 PermissionsWorkDotComUserPerm,PermissionsContentHubUser,PermissionsGovernNetworks,PermissionsSalesConsole,
                 PermissionsTwoFactorApi,PermissionsDeleteTopics,PermissionsEditTopics,PermissionsCreateTopics,PermissionsAssignTopics,
                 PermissionsIdentityEnabled,PermissionsIdentityConnect,PermissionsAllowViewKnowledge,PermissionsContentWorkspaces,
                 PermissionsManageSearchPromotionRules,PermissionsCustomMobileAppsAccess,PermissionsViewHelpLink,PermissionsManageProfilesPermissionsets,
                 PermissionsAssignPermissionSets,PermissionsManageRoles,PermissionsManageIpAddresses,PermissionsManageSharing,
                 PermissionsManageInternalUsers,PermissionsManagePasswordPolicies,PermissionsManageLoginAccessPolicies,PermissionsViewPlatformEvents,
                 PermissionsManageCustomPermissions,PermissionsCanVerifyComment,PermissionsManageUnlistedGroups,PermissionsStdAutomaticActivityCapture,
                 PermissionsInsightsAppDashboardEditor,PermissionsManageTwoFactor,PermissionsInsightsAppUser,PermissionsInsightsAppAdmin,
                 PermissionsInsightsAppEltEditor,PermissionsInsightsAppUploadUser,PermissionsInsightsCreateApplication,PermissionsLightningExperienceUser,
                 PermissionsViewDataLeakageEvents,PermissionsConfigCustomRecs,PermissionsSubmitMacrosAllowed,PermissionsBulkMacrosAllowed,
                 PermissionsShareInternalArticles,PermissionsManageSessionPermissionSets,PermissionsManageTemplatedApp,PermissionsUseTemplatedApp,
                 PermissionsSendAnnouncementEmails,PermissionsChatterEditOwnPost,PermissionsChatterEditOwnRecordPost,PermissionsWaveTabularDownload,
                 PermissionsAutomaticActivityCapture,PermissionsImportCustomObjects,PermissionsDelegatedTwoFactor,PermissionsChatterComposeUiCodesnippet,
                 PermissionsSelectFilesFromSalesforce,PermissionsModerateNetworkUsers,PermissionsMergeTopics,PermissionsSubscribeToLightningReports,
                 PermissionsManagePvtRptsAndDashbds,PermissionsAllowLightningLogin,PermissionsCampaignInfluence2,PermissionsViewDataAssessment,
                 PermissionsRemoveDirectMessageMembers,PermissionsCanApproveFeedPost,PermissionsAddDirectMessageMembers,PermissionsAllowViewEditConvertedLeads,
                 PermissionsShowCompanyNameAsUserBadge,PermissionsAccessCMC,PermissionsViewHealthCheck,PermissionsManageHealthCheck,
                 PermissionsPackaging2,PermissionsManageCertificates,PermissionsCreateReportInLightning,PermissionsPreventClassicExperience,
                 PermissionsHideReadByList,PermissionsListEmailSend,PermissionsFeedPinning,PermissionsChangeDashboardColors,
                 PermissionsManageRecommendationStrategies,PermissionsManagePropositions,PermissionsCloseConversations,PermissionsSubscribeReportRolesGrps,
                 PermissionsSubscribeDashboardRolesGrps,PermissionsUseWebLink,PermissionsHasUnlimitedNBAExecutions,PermissionsViewOnlyEmbeddedAppUser,
                 PermissionsViewAllActivities,PermissionsSubscribeReportToOtherUsers,PermissionsLightningConsoleAllowedForUser,
                 PermissionsSubscribeReportsRunAsUser,PermissionsSubscribeToLightningDashboards,PermissionsSubscribeDashboardToOtherUsers,
                 PermissionsCreateLtngTempInPub,PermissionsAppointmentBookingUserAccess,PermissionsTransactionalEmailSend,
                 PermissionsViewPrivateStaticResources,PermissionsCreateLtngTempFolder,PermissionsApexRestServices,PermissionsConfigureLiveMessage,
                 PermissionsLiveMessageAgent,PermissionsEnableCommunityAppLauncher,PermissionsGiveRecognitionBadge,PermissionsLightningSchedulerUserAccess,
                 PermissionsUseMySearch,PermissionsLtngPromoReserved01UserPerm,PermissionsManageSubscriptions,PermissionsWaveManagePrivateAssetsUser,
                 PermissionsCanEditDataPrepRecipe,PermissionsAddAnalyticsRemoteConnections,PermissionsManageSurveys,PermissionsUseAssistantDialog,
                 PermissionsUseQuerySuggestions,PermissionsPackaging2PromoteVersion,PermissionsRecordVisibilityAPI,PermissionsViewRoles,
                 PermissionsCanManageMaps,PermissionsLMOutboundMessagingUserPerm,PermissionsModifyDataClassification,PermissionsPrivacyDataAccess,
                 PermissionsQueryAllFiles,PermissionsModifyMetadata,PermissionsManageCMS,PermissionsSandboxTestingInCommunityApp,
                 PermissionsCanEditPrompts,PermissionsViewUserPII,PermissionsManageHubConnections,PermissionsB2BMarketingAnalyticsUser,
                 PermissionsTraceXdsQueries,PermissionsViewSecurityCommandCenter,PermissionsManageSecurityCommandCenter,PermissionsViewAllCustomSettings,
                 PermissionsViewAllForeignKeyNames,PermissionsAddWaveNotificationRecipients,PermissionsHeadlessCMSAccess,PermissionsLMEndMessagingSessionUserPerm,
                 PermissionsConsentApiUpdate,PermissionsPaymentsAPIUser,PermissionsAccessContentBuilder,PermissionsAccountSwitcherUser,
                 PermissionsViewAnomalyEvents,PermissionsManageC360AConnections,PermissionsIsContactCenterAdmin,PermissionsIsContactCenterAgent,
                 PermissionsManageReleaseUpdates,PermissionsViewAllProfiles,PermissionsSkipIdentityConfirmation,PermissionsCanToggleCallRecordings,
                 PermissionsLearningManager,PermissionsSendCustomNotifications,PermissionsPackaging2Delete,PermissionsUseOmnichannelInventoryAPIs,
                 PermissionsViewRestrictionAndScopingRules,PermissionsFSCComprehensiveUserAccess,PermissionsBotManageBots,
                 PermissionsBotManageBotsTrainingData,PermissionsSchedulingLineAmbassador,PermissionsSchedulingFacilityManager,
                 PermissionsOmnichannelInventorySync,PermissionsManageLearningReporting,PermissionsIsContactCenterSupervisor,
                 PermissionsIsotopeCToCUser,PermissionsCanAccessCE,PermissionsUseAddOrderItemSummaryAPIs,PermissionsIsotopeAccess,
                 PermissionsIsotopeLEX,PermissionsQuipMetricsAccess,PermissionsQuipUserEngagementMetrics,PermissionsRemoteMediaVirtualDesktop,
                 PermissionsTransactionSecurityExempt,PermissionsManageStores,PermissionsManageExternalConnections,PermissionsUseReturnOrder,
                 PermissionsUseReturnOrderAPIs,PermissionsUseSubscriptionEmails,PermissionsUseOrderEntry,PermissionsUseRepricing,
                 PermissionsAIViewInsightObjects,PermissionsAICreateInsightObjects,PermissionsViewMLModels,PermissionsLifecycleManagementAPIUser,
                 PermissionsNativeWebviewScrolling,PermissionsViewDeveloperName,PermissionsBypassMFAForUiLogins,PermissionsClientSecretRotation,
                 PermissionsAccessToServiceProcess,PermissionsManageOrchInstsAndWorkItems,PermissionsManageDataspaceScope,PermissionsConfigureDataspaceScope,
                 PermissionsEditRepricing,PermissionsEnableIPFSUpload,PermissionsEnableBCTransactionPolling,PermissionsFSCArcGraphCommunityUser,
                 LastViewedDate,Name,UserLicenseId,UserType,CreatedDate,CreatedById,LastModifiedDate,LastModifiedById,SystemModstamp

              """

    entity = "Profile"
    name = "profiles"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Description", StringType),
        Property("LastReferencedDate", StringType),
        Property("PermissionsEmailSingle", BooleanType),
        Property("PermissionsEmailMass", BooleanType),
        Property("PermissionsEditTask", BooleanType),
        Property("PermissionsEditEvent", BooleanType),
        Property("PermissionsExportReport", BooleanType),
        Property("PermissionsImportPersonal", BooleanType),
        Property("PermissionsDataExport", BooleanType),
        Property("PermissionsManageUsers", BooleanType),
        Property("PermissionsEditPublicFilters", BooleanType),
        Property("PermissionsEditPublicTemplates", BooleanType),
        Property("PermissionsModifyAllData", BooleanType),
        Property("PermissionsEditBillingInfo", BooleanType),
        Property("PermissionsManageCases", BooleanType),
        Property("PermissionsMassInlineEdit", BooleanType),
        Property("PermissionsEditKnowledge", BooleanType),
        Property("PermissionsManageKnowledge", BooleanType),
        Property("PermissionsManageSolutions", BooleanType),
        Property("PermissionsCustomizeApplication", BooleanType),
        Property("PermissionsEditReadonlyFields", BooleanType),
        Property("PermissionsRunReports", BooleanType),
        Property("PermissionsViewSetup", BooleanType),
        Property("PermissionsTransferAnyEntity", BooleanType),
        Property("PermissionsNewReportBuilder", BooleanType),
        Property("PermissionsActivateContract", BooleanType),
        Property("PermissionsActivateOrder", BooleanType),
        Property("PermissionsImportLeads", BooleanType),
        Property("PermissionsManageLeads", BooleanType),
        Property("PermissionsTransferAnyLead", BooleanType),
        Property("PermissionsViewAllData", BooleanType),
        Property("PermissionsEditPublicDocuments", BooleanType),
        Property("PermissionsViewEncryptedData", BooleanType),
        Property("PermissionsEditBrandTemplates", BooleanType),
        Property("PermissionsEditHtmlTemplates", BooleanType),
        Property("PermissionsChatterInternalUser", BooleanType),
        Property("PermissionsManageEncryptionKeys", BooleanType),
        Property("PermissionsDeleteActivatedContract", BooleanType),
        Property("PermissionsChatterInviteExternalUsers", BooleanType),
        Property("PermissionsSendSitRequests", BooleanType),
        Property("PermissionsApiUserOnly", BooleanType),
        Property("PermissionsManageRemoteAccess", BooleanType),
        Property("PermissionsCanUseNewDashboardBuilder", BooleanType),
        Property("PermissionsManageCategories", BooleanType),
        Property("PermissionsConvertLeads", BooleanType),
        Property("PermissionsPasswordNeverExpires", BooleanType),
        Property("PermissionsUseTeamReassignWizards", BooleanType),
        Property("PermissionsEditActivatedOrders", BooleanType),
        Property("PermissionsInstallMultiforce", BooleanType),
        Property("PermissionsPublishMultiforce", BooleanType),
        Property("PermissionsChatterOwnGroups", BooleanType),
        Property("PermissionsEditOppLineItemUnitPrice", BooleanType),
        Property("PermissionsCreateMultiforce", BooleanType),
        Property("PermissionsBulkApiHardDelete", BooleanType),
        Property("PermissionsSolutionImport", BooleanType),
        Property("PermissionsManageCallCenters", BooleanType),
        Property("PermissionsManageSynonyms", BooleanType),
        Property("PermissionsViewContent", BooleanType),
        Property("PermissionsManageEmailClientConfig", BooleanType),
        Property("PermissionsEnableNotifications", BooleanType),
        Property("PermissionsManageDataIntegrations", BooleanType),
        Property("PermissionsDistributeFromPersWksp", BooleanType),
        Property("PermissionsViewDataCategories", BooleanType),
        Property("PermissionsManageDataCategories", BooleanType),
        Property("PermissionsAuthorApex", BooleanType),
        Property("PermissionsManageMobile", BooleanType),
        Property("PermissionsApiEnabled", BooleanType),
        Property("PermissionsManageCustomReportTypes", BooleanType),
        Property("PermissionsEditCaseComments", BooleanType),
        Property("PermissionsTransferAnyCase", BooleanType),
        Property("PermissionsContentAdministrator", BooleanType),
        Property("PermissionsCreateWorkspaces", BooleanType),
        Property("PermissionsManageContentPermissions", BooleanType),
        Property("PermissionsManageContentProperties", BooleanType),
        Property("PermissionsManageContentTypes", BooleanType),
        Property("PermissionsManageExchangeConfig", BooleanType),
        Property("PermissionsManageAnalyticSnapshots", BooleanType),
        Property("PermissionsScheduleReports", BooleanType),
        Property("PermissionsManageBusinessHourHolidays", BooleanType),
        Property("PermissionsManageEntitlements", BooleanType),
        Property("PermissionsManageDynamicDashboards", BooleanType),
        Property("PermissionsCustomSidebarOnAllPages", BooleanType),
        Property("PermissionsManageInteraction", BooleanType),
        Property("PermissionsViewMyTeamsDashboards", BooleanType),
        Property("PermissionsModerateChatter", BooleanType),
        Property("PermissionsResetPasswords", BooleanType),
        Property("PermissionsFlowUFLRequired", BooleanType),
        Property("PermissionsCanInsertFeedSystemFields", BooleanType),
        Property("PermissionsActivitiesAccess", BooleanType),
        Property("PermissionsManageKnowledgeImportExport", BooleanType),
        Property("PermissionsEmailTemplateManagement", BooleanType),
        Property("PermissionsEmailAdministration", BooleanType),
        Property("PermissionsManageChatterMessages", BooleanType),
        Property("PermissionsAllowEmailIC", BooleanType),
        Property("PermissionsChatterFileLink", BooleanType),
        Property("PermissionsForceTwoFactor", BooleanType),
        Property("PermissionsViewEventLogFiles", BooleanType),
        Property("PermissionsManageNetworks", BooleanType),
        Property("PermissionsManageAuthProviders", BooleanType),
        Property("PermissionsRunFlow", BooleanType),
        Property("PermissionsCreateCustomizeDashboards", BooleanType),
        Property("PermissionsCreateDashboardFolders", BooleanType),
        Property("PermissionsViewPublicDashboards", BooleanType),
        Property("PermissionsManageDashbdsInPubFolders", BooleanType),
        Property("PermissionsCreateCustomizeReports", BooleanType),
        Property("PermissionsCreateReportFolders", BooleanType),
        Property("PermissionsViewPublicReports", BooleanType),
        Property("PermissionsManageReportsInPubFolders", BooleanType),
        Property("PermissionsEditMyDashboards", BooleanType),
        Property("PermissionsEditMyReports", BooleanType),
        Property("PermissionsViewAllUsers", BooleanType),
        Property("PermissionsAllowUniversalSearch", BooleanType),
        Property("PermissionsConnectOrgToEnvironmentHub", BooleanType),
        Property("PermissionsWorkCalibrationUser", BooleanType),
        Property("PermissionsCreateCustomizeFilters", BooleanType),
        Property("PermissionsWorkDotComUserPerm", BooleanType),
        Property("PermissionsContentHubUser", BooleanType),
        Property("PermissionsGovernNetworks", BooleanType),
        Property("PermissionsSalesConsole", BooleanType),
        Property("PermissionsTwoFactorApi", BooleanType),
        Property("PermissionsDeleteTopics", BooleanType),
        Property("PermissionsEditTopics", BooleanType),
        Property("PermissionsCreateTopics", BooleanType),
        Property("PermissionsAssignTopics", BooleanType),
        Property("PermissionsIdentityEnabled", BooleanType),
        Property("PermissionsIdentityConnect", BooleanType),
        Property("PermissionsAllowViewKnowledge", BooleanType),
        Property("PermissionsContentWorkspaces", BooleanType),
        Property("PermissionsManageSearchPromotionRules", BooleanType),
        Property("PermissionsCustomMobileAppsAccess", BooleanType),
        Property("PermissionsViewHelpLink", BooleanType),
        Property("PermissionsManageProfilesPermissionsets", BooleanType),
        Property("PermissionsAssignPermissionSets", BooleanType),
        Property("PermissionsManageRoles", BooleanType),
        Property("PermissionsManageIpAddresses", BooleanType),
        Property("PermissionsManageSharing", BooleanType),
        Property("PermissionsManageInternalUsers", BooleanType),
        Property("PermissionsManagePasswordPolicies", BooleanType),
        Property("PermissionsManageLoginAccessPolicies", BooleanType),
        Property("PermissionsViewPlatformEvents", BooleanType),
        Property("PermissionsManageCustomPermissions", BooleanType),
        Property("PermissionsCanVerifyComment", BooleanType),
        Property("PermissionsManageUnlistedGroups", BooleanType),
        Property("PermissionsStdAutomaticActivityCapture", BooleanType),
        Property("PermissionsInsightsAppDashboardEditor", BooleanType),
        Property("PermissionsManageTwoFactor", BooleanType),
        Property("PermissionsInsightsAppUser", BooleanType),
        Property("PermissionsInsightsAppAdmin", BooleanType),
        Property("PermissionsInsightsAppEltEditor", BooleanType),
        Property("PermissionsInsightsAppUploadUser", BooleanType),
        Property("PermissionsInsightsCreateApplication", BooleanType),
        Property("PermissionsLightningExperienceUser", BooleanType),
        Property("PermissionsViewDataLeakageEvents", BooleanType),
        Property("PermissionsConfigCustomRecs", BooleanType),
        Property("PermissionsSubmitMacrosAllowed", BooleanType),
        Property("PermissionsBulkMacrosAllowed", BooleanType),
        Property("PermissionsShareInternalArticles", BooleanType),
        Property("PermissionsManageSessionPermissionSets", BooleanType),
        Property("PermissionsManageTemplatedApp", BooleanType),
        Property("PermissionsUseTemplatedApp", BooleanType),
        Property("PermissionsSendAnnouncementEmails", BooleanType),
        Property("PermissionsChatterEditOwnPost", BooleanType),
        Property("PermissionsChatterEditOwnRecordPost", BooleanType),
        Property("PermissionsWaveTabularDownload", BooleanType),
        Property("PermissionsAutomaticActivityCapture", BooleanType),
        Property("PermissionsImportCustomObjects", BooleanType),
        Property("PermissionsDelegatedTwoFactor", BooleanType),
        Property("PermissionsChatterComposeUiCodesnippet", BooleanType),
        Property("PermissionsSelectFilesFromSalesforce", BooleanType),
        Property("PermissionsModerateNetworkUsers", BooleanType),
        Property("PermissionsMergeTopics", BooleanType),
        Property("PermissionsSubscribeToLightningReports", BooleanType),
        Property("PermissionsManagePvtRptsAndDashbds", BooleanType),
        Property("PermissionsAllowLightningLogin", BooleanType),
        Property("PermissionsCampaignInfluence2", BooleanType),
        Property("PermissionsViewDataAssessment", BooleanType),
        Property("PermissionsRemoveDirectMessageMembers", BooleanType),
        Property("PermissionsCanApproveFeedPost", BooleanType),
        Property("PermissionsAddDirectMessageMembers", BooleanType),
        Property("PermissionsAllowViewEditConvertedLeads", BooleanType),
        Property("PermissionsShowCompanyNameAsUserBadge", BooleanType),
        Property("PermissionsAccessCMC", BooleanType),
        Property("PermissionsViewHealthCheck", BooleanType),
        Property("PermissionsManageHealthCheck", BooleanType),
        Property("PermissionsPackaging2", BooleanType),
        Property("PermissionsManageCertificates", BooleanType),
        Property("PermissionsCreateReportInLightning", BooleanType),
        Property("PermissionsPreventClassicExperience", BooleanType),
        Property("PermissionsHideReadByList", BooleanType),
        Property("PermissionsListEmailSend", BooleanType),
        Property("PermissionsFeedPinning", BooleanType),
        Property("PermissionsChangeDashboardColors", BooleanType),
        Property("PermissionsManageRecommendationStrategies", BooleanType),
        Property("PermissionsManagePropositions", BooleanType),
        Property("PermissionsCloseConversations", BooleanType),
        Property("PermissionsSubscribeReportRolesGrps", BooleanType),
        Property("PermissionsSubscribeDashboardRolesGrps", BooleanType),
        Property("PermissionsUseWebLink", BooleanType),
        Property("PermissionsHasUnlimitedNBAExecutions", BooleanType),
        Property("PermissionsViewOnlyEmbeddedAppUser", BooleanType),
        Property("PermissionsViewAllActivities", BooleanType),
        Property("PermissionsSubscribeReportToOtherUsers", BooleanType),
        Property("PermissionsLightningConsoleAllowedForUser", BooleanType),
        Property("PermissionsSubscribeReportsRunAsUser", BooleanType),
        Property("PermissionsSubscribeToLightningDashboards", BooleanType),
        Property("PermissionsSubscribeDashboardToOtherUsers", BooleanType),
        Property("PermissionsCreateLtngTempInPub", BooleanType),
        Property("PermissionsAppointmentBookingUserAccess", BooleanType),
        Property("PermissionsTransactionalEmailSend", BooleanType),
        Property("PermissionsViewPrivateStaticResources", BooleanType),
        Property("PermissionsCreateLtngTempFolder", BooleanType),
        Property("PermissionsApexRestServices", BooleanType),
        Property("PermissionsConfigureLiveMessage", BooleanType),
        Property("PermissionsLiveMessageAgent", BooleanType),
        Property("PermissionsEnableCommunityAppLauncher", BooleanType),
        Property("PermissionsGiveRecognitionBadge", BooleanType),
        Property("PermissionsLightningSchedulerUserAccess", BooleanType),
        Property("PermissionsUseMySearch", BooleanType),
        Property("PermissionsLtngPromoReserved01UserPerm", BooleanType),
        Property("PermissionsManageSubscriptions", BooleanType),
        Property("PermissionsWaveManagePrivateAssetsUser", BooleanType),
        Property("PermissionsCanEditDataPrepRecipe", BooleanType),
        Property("PermissionsAddAnalyticsRemoteConnections", BooleanType),
        Property("PermissionsManageSurveys", BooleanType),
        Property("PermissionsUseAssistantDialog", BooleanType),
        Property("PermissionsUseQuerySuggestions", BooleanType),
        Property("PermissionsPackaging2PromoteVersion", BooleanType),
        Property("PermissionsRecordVisibilityAPI", BooleanType),
        Property("PermissionsViewRoles", BooleanType),
        Property("PermissionsCanManageMaps", BooleanType),
        Property("PermissionsLMOutboundMessagingUserPerm", BooleanType),
        Property("PermissionsModifyDataClassification", BooleanType),
        Property("PermissionsPrivacyDataAccess", BooleanType),
        Property("PermissionsQueryAllFiles", BooleanType),
        Property("PermissionsModifyMetadata", BooleanType),
        Property("PermissionsManageCMS", BooleanType),
        Property("PermissionsSandboxTestingInCommunityApp", BooleanType),
        Property("PermissionsCanEditPrompts", BooleanType),
        Property("PermissionsViewUserPII", BooleanType),
        Property("PermissionsManageHubConnections", BooleanType),
        Property("PermissionsB2BMarketingAnalyticsUser", BooleanType),
        Property("PermissionsTraceXdsQueries", BooleanType),
        Property("PermissionsViewSecurityCommandCenter", BooleanType),
        Property("PermissionsManageSecurityCommandCenter", BooleanType),
        Property("PermissionsViewAllCustomSettings", BooleanType),
        Property("PermissionsViewAllForeignKeyNames", BooleanType),
        Property("PermissionsAddWaveNotificationRecipients", BooleanType),
        Property("PermissionsHeadlessCMSAccess", BooleanType),
        Property("PermissionsLMEndMessagingSessionUserPerm", BooleanType),
        Property("PermissionsConsentApiUpdate", BooleanType),
        Property("PermissionsPaymentsAPIUser", BooleanType),
        Property("PermissionsAccessContentBuilder", BooleanType),
        Property("PermissionsAccountSwitcherUser", BooleanType),
        Property("PermissionsViewAnomalyEvents", BooleanType),
        Property("PermissionsManageC360AConnections", BooleanType),
        Property("PermissionsIsContactCenterAdmin", BooleanType),
        Property("PermissionsIsContactCenterAgent", BooleanType),
        Property("PermissionsManageReleaseUpdates", BooleanType),
        Property("PermissionsViewAllProfiles", BooleanType),
        Property("PermissionsSkipIdentityConfirmation", BooleanType),
        Property("PermissionsCanToggleCallRecordings", BooleanType),
        Property("PermissionsLearningManager", BooleanType),
        Property("PermissionsSendCustomNotifications", BooleanType),
        Property("PermissionsPackaging2Delete", BooleanType),
        Property("PermissionsUseOmnichannelInventoryAPIs", BooleanType),
        Property("PermissionsViewRestrictionAndScopingRules", BooleanType),
        Property("PermissionsFSCComprehensiveUserAccess", BooleanType),
        Property("PermissionsBotManageBots", BooleanType),
        Property("PermissionsBotManageBotsTrainingData", BooleanType),
        Property("PermissionsSchedulingLineAmbassador", BooleanType),
        Property("PermissionsSchedulingFacilityManager", BooleanType),
        Property("PermissionsOmnichannelInventorySync", BooleanType),
        Property("PermissionsManageLearningReporting", BooleanType),
        Property("PermissionsIsContactCenterSupervisor", BooleanType),
        Property("PermissionsIsotopeCToCUser", BooleanType),
        Property("PermissionsCanAccessCE", BooleanType),
        Property("PermissionsUseAddOrderItemSummaryAPIs", BooleanType),
        Property("PermissionsIsotopeAccess", BooleanType),
        Property("PermissionsIsotopeLEX", BooleanType),
        Property("PermissionsQuipMetricsAccess", BooleanType),
        Property("PermissionsQuipUserEngagementMetrics", BooleanType),
        Property("PermissionsRemoteMediaVirtualDesktop", BooleanType),
        Property("PermissionsTransactionSecurityExempt", BooleanType),
        Property("PermissionsManageStores", BooleanType),
        Property("PermissionsManageExternalConnections", BooleanType),
        Property("PermissionsUseReturnOrder", BooleanType),
        Property("PermissionsUseReturnOrderAPIs", BooleanType),
        Property("PermissionsUseSubscriptionEmails", BooleanType),
        Property("PermissionsUseOrderEntry", BooleanType),
        Property("PermissionsUseRepricing", BooleanType),
        Property("PermissionsAIViewInsightObjects", BooleanType),
        Property("PermissionsAICreateInsightObjects", BooleanType),
        Property("PermissionsViewMLModels", BooleanType),
        Property("PermissionsLifecycleManagementAPIUser", BooleanType),
        Property("PermissionsNativeWebviewScrolling", BooleanType),
        Property("PermissionsViewDeveloperName", BooleanType),
        Property("PermissionsBypassMFAForUiLogins", BooleanType),
        Property("PermissionsClientSecretRotation", BooleanType),
        Property("PermissionsAccessToServiceProcess", BooleanType),
        Property("PermissionsManageOrchInstsAndWorkItems", BooleanType),
        Property("PermissionsManageDataspaceScope", BooleanType),
        Property("PermissionsConfigureDataspaceScope", BooleanType),
        Property("PermissionsEditRepricing", BooleanType),
        Property("PermissionsEnableIPFSUpload", BooleanType),
        Property("PermissionsEnableBCTransactionPolling", BooleanType),
        Property("PermissionsFSCArcGraphCommunityUser", BooleanType),
        Property("LastViewedDate", StringType),
        Property("Name", StringType),
        Property("UserLicenseId", StringType),
        Property("UserType", StringType),
        Property("CreatedDate", StringType),
        Property("CreatedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"
        return params


class OpportunityHistoryStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_opportunityhistory.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    columns = """
                 Id, CreatedById, CreatedDate, SystemModstamp, Amount, CloseDate, ExpectedRevenue, ForecastCategory, IsDeleted, OpportunityId, PrevAmount, PrevCloseDate, Probability, StageName
              """

    entity = "OpportunityHistory"
    name = "opportunity_history"
    path = "/query"
    primary_keys = ["Id"]
    replication_key = "CreatedDate"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("Id", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("SystemModstamp", StringType),
        Property("Amount", NumberType),
        Property("CloseDate", StringType),
        Property("ExpectedRevenue", NumberType),
        Property("ForecastCategory", StringType),
        Property("IsDeleted", BooleanType),
        Property("OpportunityId", StringType),
        Property("PrevAmount", StringType),
        Property("PrevCloseDate", StringType),
        Property("Probability", NumberType),
        Property("StageName", StringType),
    ).to_dict()

    def get_url_params(
        self, context: dict | None, next_page_token: t.Any
    ):  # noqa: ANN401, E501
        params = super().get_url_params(context, next_page_token)
        params["q"] = f"SELECT {self.columns} FROM {self.entity}"  # noqa: S608
        return params


class BulkOpportunityHistoryStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_opportunityhistory.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "opportunity_history_bulk"
    path = ""
    replication_key = "CreatedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("SystemModstamp", StringType),
        Property("Amount", NumberType),
        Property("CloseDate", StringType),
        Property("ExpectedRevenue", NumberType),
        Property("ForecastCategory", StringType),
        Property("IsDeleted", BooleanType),
        Property("OpportunityId", StringType),
        Property("PrevAmount", StringType),
        Property("PrevCloseDate", StringType),
        Property("Probability", NumberType),
        Property("StageName", StringType),
        Property("AccountId", StringType),
        Property("CampaignId", StringType),
        Property("ContactId", StringType),
        Property("Description", StringType),
        Property("Fiscal", StringType),
        Property("FiscalQuarter", StringType),
        Property("FiscalYear", StringType),
        Property("ForecastCategoryName", StringType),
        Property("HasOpenActivity", BooleanType),
        Property("HasOpportunityLineItem", BooleanType),
        Property("HasOverdueTask", BooleanType),
        Property("IsPrivate", BooleanType),
        Property("IsWon", BooleanType),
        Property("IsClosed", BooleanType),
        Property("LastActivityDate", StringType),
        Property("LastAmountChangedHistoryId", StringType),
        Property("LastCloseDateChangedHistoryId", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastStageChangeDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LeadSource", StringType),
        Property("Name", StringType),
        Property("NextStep", StringType),
        Property("OwnerId", StringType),
        Property("Pricebook2Id", StringType),
        Property("PushCount", NumberType),
        Property("TotalOpportunityQuantity", StringType),
        Property("Type", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with NumberType
        number_columns = [
            "Amount",
            "ExpectedRevenue",
            "Probability",
            "PushCount",
        ]

        for column in number_columns:
            row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          AccountId, Amount, CampaignID, CloseDate, ContactId, CreatedById, CreatedDate, Description, ExpectedRevenue, Fiscal,
                          FiscalQuarter, FiscalYear, ForecastCategory, ForecastCategoryName, HasOpenActivity, HasOpportunityLineItem, 
                          HasOverDueTask, Id, IsClosed, IsDeleted, IsPrivate, IsWon, LastActivityDate, LastAmountChangedHistoryId, 
                          LastCloseDateChangedHistoryId, LastModifiedById, LastModifiedDate, LastReferencedDate, LastStageChangeDate, 
                          LastVieweddate, LeadSource, Name, NextStep, OwnerId, Pricebook2Id, Probability, PushCount, StageName, 
                          SystemModstamp, TotalOpportunityQuantity, Type
                      """
            entity = "OPPORTUNITY"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "opportunity_history_bulk"
            path = ""
            primary_keys = ["Id"]

            @property
            def url_base(self):
                domain = self.config["domain"]
                return f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            self.logger.info(e)


class BulkAccountStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_account.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    entity = "Account"
    name = "accounts_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("YearStarted", StringType),
        Property("AccountNumber", StringType),
        Property("AccountSource", StringType),
        Property("AnnualRevenue", NumberType),
        Property("city", StringType),
        Property("country", StringType),
        Property("geocodeAccuracy", StringType),
        Property("latitude", StringType),
        Property("longitude", StringType),
        Property("postalCode", StringType),
        Property("state", StringType),
        Property("street", StringType),
        Property("BillingCity", StringType),
        Property("BillingCountry", StringType),
        Property("BillingLatitude", StringType),
        Property("BillingLongitude", StringType),
        Property("BillingPostalCode", StringType),
        Property("BillingState", StringType),
        Property("BillingStreet", StringType),
        Property("BillingGeocodeAccuracy", StringType),
        Property("CleanStatus", StringType),
        Property("Description", StringType),
        Property("DunsNumber", StringType),
        Property("Fax", StringType),
        Property("Industry", StringType),
        Property("Jigsaw", StringType),
        Property("LastActivityDate", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("MasterRecordId", StringType),
        Property("NaicsCode", StringType),
        Property("NaicsDesc", StringType),
        Property("NumberOfEmployees", IntegerType),
        Property("OperatingHoursId", StringType),
        Property("OwnerId", StringType),
        Property("Ownership", StringType),
        Property("ParentId", StringType),
        Property("Phone", StringType),
        Property("PhotoUrl", StringType),
        Property("Rating", StringType),
        Property("city", StringType),
        Property("country", StringType),
        Property("geocodeAccuracy", StringType),
        Property("latitude", StringType),
        Property("longitude", StringType),
        Property("postalCode", StringType),
        Property("state", StringType),
        Property("street", StringType),
        Property("ShippingCity", StringType),
        Property("ShippingCountry", StringType),
        Property("ShippingGeocodeAccuracy", StringType),
        Property("ShippingLatitude", StringType),
        Property("ShippingLongitude", StringType),
        Property("ShippingPostalCode", StringType),
        Property("ShippingState", StringType),
        Property("ShippingStreet", StringType),
        Property("Sic", StringType),
        Property("SicDesc", StringType),
        Property("Site", StringType),
        Property("TickerSymbol", StringType),
        Property("Tradestyle", StringType),
        Property("Type", StringType),
        Property("Website", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("DandbCompanyId", StringType),
        Property("IsDeleted", BooleanType),
        Property("JigsawCompanyId", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        return f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with NumberType
        number_columns = [
            "AnnualRevenue",
            "NumberOfEmployees",
        ]

        for column in number_columns:
            row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,YearStarted,AccountNumber,AccountSource,AnnualRevenue,BillingCity,BillingCountry,
                          BillingLatitude,BillingLongitude,BillingPostalCode,BillingState,BillingStreet,BillingGeocodeAccuracy,
                          CleanStatus,Description,DunsNumber,Fax,Industry,Jigsaw,LastActivityDate,LastReferencedDate,LastViewedDate,
                          MasterRecordId,NaicsCode,NaicsDesc,NumberOfEmployees,OperatingHoursId,OwnerId,Ownership,ParentId,Phone,
                          PhotoUrl,Rating,ShippingCity,ShippingCountry,ShippingGeocodeAccuracy,ShippingLatitude,
                          ShippingLongitude,ShippingPostalCode,ShippingState,ShippingStreet,Sic,SicDesc,Site,TickerSymbol,Tradestyle,Type,
                          Website,CreatedById,CreatedDate,DandbCompanyId,IsDeleted,JigsawCompanyId,
                          LastModifiedById,LastModifiedDate,SystemModstamp
                      """
            entity = "ACCOUNT"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "accounts_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkContactStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_contact.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "contacts_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("AccountId", StringType),
        Property("AssistantName", StringType),
        Property("AssistantPhone", StringType),
        Property("Birthdate", StringType),
        Property("CleanStatus", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Department", StringType),
        Property("Description", StringType),
        Property("Email", StringType),
        Property("EmailBouncedDate", StringType),
        Property("EmailBouncedReason", StringType),
        Property("Fax", StringType),
        Property("FirstName", StringType),
        Property("LastName", StringType),
        Property("HomePhone", StringType),
        Property("IndividualId", StringType),
        Property("IsDeleted", BooleanType),
        Property("IsEmailBounced", BooleanType),
        Property("Jigsaw", StringType),
        Property("JigsawContactId", StringType),
        Property("LastActivityDate", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastCURequestDate", StringType),
        Property("LastCUUpdateDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("LeadSource", StringType),
        Property("city", StringType),
        Property("country", StringType),
        Property("geocodeAccuracy", StringType),
        Property("latitude", StringType),
        Property("longitude", StringType),
        Property("postalCode", StringType),
        Property("state", StringType),
        Property("street", StringType),
        Property("MailingCity", StringType),
        Property("MailingCountry", StringType),
        Property("MailingGeocodeAccuracy", StringType),
        Property("MailingLatitude", StringType),
        Property("MailingLongitude", StringType),
        Property("MailingPostalCode", StringType),
        Property("MailingState", StringType),
        Property("MailingStreet", StringType),
        Property("MasterRecordId", StringType),
        Property("MobilePhone", StringType),
        Property("city", StringType),
        Property("country", StringType),
        Property("geocodeAccuracy", StringType),
        Property("latitude", StringType),
        Property("longitude", StringType),
        Property("postalCode", StringType),
        Property("state", StringType),
        Property("street", StringType),
        Property("OtherCity", StringType),
        Property("OtherCountry", StringType),
        Property("OtherGeocodeAccuracy", StringType),
        Property("OtherLatitude", StringType),
        Property("OtherLongitude", StringType),
        Property("OtherPhone", StringType),
        Property("OtherPostalCode", StringType),
        Property("OtherState", StringType),
        Property("OtherStreet", StringType),
        Property("OwnerId", StringType),
        Property("Phone", StringType),
        Property("PhotoUrl", StringType),
        Property("ReportsToId", BooleanType),
        Property("Salutation", StringType),
        Property("SystemModstamp", StringType),
        Property("Title", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]
            columns = """
                         Id,Name,AccountId,AssistantName,AssistantPhone,Birthdate,CleanStatus,CreatedById,CreatedDate,Department,
                         Description,Email,EmailBouncedDate,EmailBouncedReason,Fax,FirstName,LastName,HomePhone,IndividualId,IsDeleted,
                         IsEmailBounced,Jigsaw,JigsawContactId,LastActivityDate,LastReferencedDate,LastViewedDate,LastCURequestDate,
                         LastCUUpdateDate,LastModifiedById,LastModifiedDate,LeadSource,MailingCity,MailingCountry,
                         MailingGeocodeAccuracy,MailingLatitude,MailingLongitude,MailingPostalCode,MailingState,MailingStreet,MasterRecordId,
                         MobilePhone,OtherCity,OtherCountry,OtherGeocodeAccuracy,OtherLatitude,OtherLongitude,OtherPhone,OtherPostalCode,
                         OtherState,OtherStreet,OwnerId,Phone,PhotoUrl,ReportsToId,Salutation,SystemModstamp,Title
                      """
            entity = "CONTACT"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "contacts_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)


class BulkCampaignStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_campaign.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "campaigns_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("ActualCost", NumberType),
        Property("AmountAllOpportunities", NumberType),
        Property("AmountWonOpportunities", NumberType),
        Property("BudgetedCost", NumberType),
        Property("CampaignMemberRecordTypeId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("EndDate", StringType),
        Property("ExpectedResponse", NumberType),
        Property("ExpectedRevenue", NumberType),
        Property("IsActive", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("LastActivityDate", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", BooleanType),
        Property("NumberOfContacts", IntegerType),
        Property("NumberOfConvertedLeads", IntegerType),
        Property("NumberOfLeads", IntegerType),
        Property("NumberOfOpportunities", IntegerType),
        Property("NumberOfResponses", IntegerType),
        Property("NumberOfWonOpportunities", IntegerType),
        Property("NumberSent", NumberType),
        Property("OwnerId", StringType),
        Property("ParentId", StringType),
        Property("StartDate", StringType),
        Property("Status", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with NumberType
        number_columns = [
            "ActualCost",
            "AmountAllOpportunities",
            "AmountWonOpportunities",
            "BudgetedCost",
            "ExpectedResponse",
            "ExpectedRevenue",
            "NumberSent",
            "NumberOfContacts",
            "NumberOfConvertedLeads",
            "NumberOfLeads",
            "NumberOfOpportunities",
            "NumberOfResponses",
            "NumberOfWonOpportunities",
        ]

        for column in number_columns:
            row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,ActualCost,AmountAllOpportunities,AmountWonOpportunities,BudgetedCost,CampaignMemberRecordTypeId,
                          CreatedById,CreatedDate,Description,EndDate,ExpectedResponse,ExpectedRevenue,IsActive,IsDeleted,LastActivityDate,
                          LastReferencedDate,LastViewedDate,LastModifiedById,LastModifiedDate,NumberOfContacts,NumberOfConvertedLeads,
                          NumberOfLeads,NumberOfOpportunities,NumberOfResponses,NumberOfWonOpportunities,NumberSent,OwnerId,ParentId,
                          StartDate,Status,Type,SystemModstamp
                      """
            entity = "CAMPAIGN"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "campaigns_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkEntitlementStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_entitlement.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "entitlements_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("AccountId", StringType),
        Property("AssetId", StringType),
        Property("BusinessHoursId", StringType),
        Property("CasesPerEntitlement", IntegerType),
        Property("ContractLineItemId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("EndDate", StringType),
        Property("IsDeleted", BooleanType),
        Property("IsPerIncident", BooleanType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("LocationId", StringType),
        Property("SvcApptBookingWindowsId", StringType),
        Property("RemainingCases", IntegerType),
        Property("RemainingWorkOrders", IntegerType),
        Property("ServiceContractId", StringType),
        Property("SlaProcessId", StringType),
        Property("StartDate", StringType),
        Property("Status", StringType),
        Property("Type", StringType),
        Property("WorkOrdersPerEntitlement", IntegerType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = [
            "CasesPerEntitlement",
            "RemainingCases",
            "RemainingWorkOrders",
            "WorkOrdersPerEntitlement",
        ]

        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])

        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,AccountId,AssetId,BusinessHoursId,CasesPerEntitlement,ContractLineItemId,CreatedById,CreatedDate,EndDate,IsDeleted,
                          IsPerIncident,LastReferencedDate,LastViewedDate,LastModifiedById,LastModifiedDate,LocationId,SvcApptBookingWindowsId,
                          RemainingCases,RemainingWorkOrders,ServiceContractId,SlaProcessId,StartDate,Status,Type,WorkOrdersPerEntitlement,SystemModstamp
                      """
            entity = "ENTITLEMENT"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "entitlements_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkCaseStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_case.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "cases_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("AccountId", StringType),
        Property("AssetId", StringType),
        Property("Comments", StringType),
        Property("CaseNumber", StringType),
        Property("ClosedDate", StringType),
        Property("ContactEmail", StringType),
        Property("ContactFax", StringType),
        Property("ContactId", StringType),
        Property("ContactMobile", StringType),
        Property("ContactPhone", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("IsClosed", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("IsEscalated", BooleanType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("MasterRecordId", StringType),
        Property("Origin", StringType),
        Property("OwnerId", StringType),
        Property("ParentId", StringType),
        Property("Priority", StringType),
        Property("Reason", StringType),
        Property("SourceId", StringType),
        Property("Status", StringType),
        Property("Subject", StringType),
        Property("SuppliedCompany", StringType),
        Property("SuppliedEmail", StringType),
        Property("SuppliedName", StringType),
        Property("SuppliedPhone", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,AccountId,AssetId,Comments,CaseNumber,ClosedDate,ContactEmail,ContactFax,ContactId,ContactMobile,ContactPhone,CreatedById,
                          CreatedDate,Description,IsClosed,IsDeleted,IsEscalated,LastReferencedDate,LastViewedDate,LastModifiedById,
                          LastModifiedDate,MasterRecordId,Origin,OwnerId,ParentId,Priority,Reason,
                          SourceId,Status,Subject,SuppliedCompany,SuppliedEmail,SuppliedName,SuppliedPhone,Type,SystemModstamp
                      """

            entity = "CASE"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "cases_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)


class BulkEmailTemplateStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_emailtemplate.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "email_templates_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("ApiVersion", NumberType),
        Property("Body", StringType),
        Property("BrandTemplateId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("DeveloperName", StringType),
        Property("Encoding", StringType),
        Property("EnhancedLetterheadId", StringType),
        Property("FolderId", StringType),
        Property("FolderName", StringType),
        Property("HtmlValue", StringType),
        Property("IsActive", BooleanType),
        Property("IsBuilderContent", BooleanType),
        Property("LastUsedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("Markup", StringType),
        Property("NamespacePrefix", StringType),
        Property("OwnerId", StringType),
        Property("RelatedEntityType", StringType),
        Property("Subject", StringType),
        Property("TemplateStyle", StringType),
        Property("TemplateType", StringType),
        Property("TimesUsed", IntegerType),
        Property("UiType", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["ApiVersion", "TimesUsed"]

        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])

        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,ApiVersion,Body,BrandTemplateId,CreatedById,CreatedDate,Description,DeveloperName,Encoding,EnhancedLetterheadId,
                          FolderId,FolderName,HtmlValue,IsActive,IsBuilderContent,LastUsedDate,LastModifiedById,LastModifiedDate,Markup,
                          NamespacePrefix,OwnerId,RelatedEntityType,Subject,TemplateStyle,TemplateType,TimesUsed,UIType,SystemModstamp
                      """
            entity = "EMAILTEMPLATE"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "email_templates_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkFolderStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_folder.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "folders_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("AccessType", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("DeveloperName", StringType),
        Property("IsReadonly", BooleanType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("NamespacePrefix", StringType),
        Property("ParentId", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,AccessType,CreatedById,CreatedDate,DeveloperName,IsReadonly,LastModifiedById,
                          LastModifiedDate,NamespacePrefix,ParentId,Type,SystemModstamp
                      """
            entity = "FOLDER"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "folders_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)


class BulkGroupStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_group.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "groups_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("DeveloperName", StringType),
        Property("DoesIncludeBosses", BooleanType),
        Property("DoesSendEmailToMembers", BooleanType),
        Property("Email", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("OwnerId", StringType),
        Property("Type", StringType),
        Property("RelatedId", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,CreatedById,CreatedDate,DeveloperName,DoesIncludeBosses,DoesSendEmailToMembers,
                          Email,LastModifiedById,LastModifiedDate,OwnerId,Type,RelatedId,SystemModstamp
                      """
            entity = "GROUP"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "groups_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)


class BulkLeadStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_lead.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "leads_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("AnnualRevenue", NumberType),
        Property("City", StringType),
        Property("CleanStatus", StringType),
        Property("Company", StringType),
        Property("CompanyDunsNumber", StringType),
        Property("ConvertedAccountId", StringType),
        Property("ConvertedContactId", StringType),
        Property("ConvertedDate", StringType),
        Property("ConvertedOpportunityId", StringType),
        Property("Country", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("DandbCompanyId", StringType),
        Property("Description", StringType),
        Property("Email", StringType),
        Property("EmailBouncedDate", StringType),
        Property("EmailBouncedReason", StringType),
        Property("Fax", StringType),
        Property("FirstName", StringType),
        Property("GeocodeAccuracy", StringType),
        Property("IndividualId", StringType),
        Property("Industry", StringType),
        Property("IsConverted", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("IsUnreadByOwner", BooleanType),
        Property("Jigsaw", StringType),
        Property("JigsawContactId", StringType),
        Property("LastActivityDate", StringType),
        Property("LastName", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("Latitude", StringType),
        Property("Longitude", StringType),
        Property("LeadSource", StringType),
        Property("MasterRecordId", StringType),
        Property("MobilePhone", StringType),
        Property("NumberOfEmployees", IntegerType),
        Property("OwnerId", StringType),
        Property("Phone", StringType),
        Property("PhotoUrl", StringType),
        Property("PostalCode", StringType),
        Property("Rating", StringType),
        Property("Salutation", StringType),
        Property("State", StringType),
        Property("Status", StringType),
        Property("Street", StringType),
        Property("Title", StringType),
        Property("Website", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["AnnualRevenue", "NumberOfEmployees"]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])

        return row

    def get_records(self, context: dict | None) -> requests.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]
            columns = """
                          Id,Name,AnnualRevenue,City,CleanStatus,Company,CompanyDunsNumber,ConvertedAccountId,ConvertedContactId,
                          ConvertedDate,ConvertedOpportunityId,Country,CreatedById,CreatedDate,DandbCompanyId,Description,
                          Email,EmailBouncedDate,EmailBouncedReason,Fax,FirstName,GeocodeAccuracy,IndividualId,Industry,IsConverted,
                          IsDeleted,IsUnreadByOwner,Jigsaw,JigsawContactId,LastActivityDate,LastName,LastReferencedDate,LastViewedDate,
                          LastModifiedById,LastModifiedDate,Latitude,Longitude,LeadSource,MasterRecordId,MobilePhone,
                          NumberOfEmployees,OwnerId,Phone,PhotoUrl,PostalCode,Rating,Salutation,
                          State,Status,Street,Title,Website,SystemModstamp
                      """
            entity = "LEAD"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "leads_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkPeriodStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_period.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "periods_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "StartDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("EndDate", StringType),
        Property("FiscalYearSettingsId", StringType),
        Property("FullyQualifiedLabel", StringType),
        Property("IsForecastPeriod", BooleanType),
        Property("Number", IntegerType),
        Property("PeriodLabel", StringType),
        Property("QuarterLabel", StringType),
        Property("StartDate", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["Number"]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,EndDate,FiscalYearSettingsId,FullyQualifiedLabel,IsForecastPeriod,
                          Number,PeriodLabel,QuarterLabel,StartDate,Type,SystemModstamp
                      """
            entity = "PERIOD"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "periods_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkSolutionStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_solution.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "solutions_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("IsDeleted", BooleanType),
        Property("IsHtml", BooleanType),
        Property("IsPublished", BooleanType),
        Property("IsPublishedInPublicKb", BooleanType),
        Property("IsReviewed", BooleanType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("OwnerId", StringType),
        Property("SolutionName", StringType),
        Property("SolutionNote", StringType),
        Property("SolutionNumber", StringType),
        Property("Status", StringType),
        Property("TimesUsed", IntegerType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["TimesUsed"]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,CreatedById,CreatedDate,IsDeleted,IsHtml,IsPublished,IsPublishedInPublicKb,IsReviewed,
                          LastReferencedDate,LastViewedDate,LastModifiedById,LastModifiedDate,OwnerId,SolutionName,
                          SolutionNote,SolutionNumber,Status,TimesUsed,SystemModstamp
                      """
            entity = "SOLUTION"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "solutions_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkStaticResourceStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_staticresource.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "static_resources_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("Body", StringType),
        Property("BodyLength", IntegerType),
        Property("CacheControl", StringType),
        Property("ContentType", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("NamespacePrefix", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["BodyLength"]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]
            columns = """
                          Id,Name,BodyLength,CacheControl,ContentType,CreatedById,CreatedDate,Description,
                          LastModifiedById,LastModifiedDate,NamespacePrefix,SystemModstamp
                      """
            entity = "STATICRESOURCE"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "static_resources_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkWebLinkStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_weblink.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "web_links_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("Body", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("DisplayType", StringType),
        Property("EncodingKey", StringType),
        Property("HasMenubar", BooleanType),
        Property("HasScrollbars", BooleanType),
        Property("HasToolbar", BooleanType),
        Property("Height", IntegerType),
        Property("IsProtected", BooleanType),
        Property("IsResizable", BooleanType),
        Property("LinkType", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("MasterLabel", StringType),
        Property("NamespacePrefix", StringType),
        Property("OpenType", StringType),
        Property("PageOrSobjectType", StringType),
        Property("Position", StringType),
        Property("RequireRowSelection", BooleanType),
        Property("ScontrolId", StringType),
        Property("ShowsLocation", BooleanType),
        Property("ShowsStatus", BooleanType),
        Property("Url", StringType),
        Property("Width", IntegerType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["Height", "Width"]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,CreatedById,CreatedDate,Description,DisplayType,EncodingKey,HasMenubar,HasScrollbars,HasToolbar,
                          Height,IsProtected,IsResizable,LinkType,LastModifiedById,LastModifiedDate,MasterLabel,NamespacePrefix,OpenType,
                          PageOrSobjectType,Position,RequireRowSelection,ScontrolId,ShowsLocation,ShowsStatus,Url,Width,SystemModstamp
                      """
            entity = "WEBLINK"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "web_links_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkPricebook2Stream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_pricebook2.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "pricebooks_2_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("IsActive", BooleanType),
        Property("IsArchived", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("IsStandard", BooleanType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,CreatedById,CreatedDate,Description,IsActive,IsArchived,IsDeleted,IsStandard,
                          LastReferencedDate,LastViewedDate,LastModifiedById,LastModifiedDate,SystemModstamp
                      """
            entity = "PRICEBOOK2"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "pricebooks_2_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)


class BulkProduct2Stream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_product2.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "products_2_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("DisplayUrl", StringType),
        Property("ExternalDataSourceId", StringType),
        Property("ExternalId", StringType),
        Property("Family", StringType),
        Property("IsActive", BooleanType),
        Property("IsArchived", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("ProductClass", StringType),
        Property("ProductCode", StringType),
        Property("QuantityUnitOfMeasure", StringType),
        Property("StockKeepingUnit", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,CreatedById,CreatedDate,Description,DisplayUrl,ExternalDataSourceId,ExternalId,Family,IsActive,IsArchived,
                          IsDeleted,LastReferencedDate,LastViewedDate,LastModifiedById,LastModifiedDate,ProductClass,ProductCode,
                          QuantityUnitOfMeasure,StockKeepingUnit,Type,SystemModstamp
                      """
            entity = "PRODUCT2"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "products_2_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)


class BulkPricebookEntryStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_pricebookentry.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "pricebook_entries_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("IsActive", BooleanType),
        Property("IsArchived", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("Pricebook2Id", StringType),
        Property("Product2Id", StringType),
        Property("ProductCode", StringType),
        Property("UnitPrice", NumberType),
        Property("UseStandardPrice", BooleanType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["UnitPrice"]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,CreatedById,CreatedDate,IsActive,IsArchived,IsDeleted,LastModifiedById,LastModifiedDate,Pricebook2Id,
                          Product2Id,ProductCode,UnitPrice,UseStandardPrice,SystemModstamp
                      """
            entity = "PRICEBOOKENTRY"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "pricebook_entries_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkUserAppInfoStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_userappinfo.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "user_app_info_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("AppDefinitionId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("FormFactor", StringType),
        Property("IsDeleted", BooleanType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("UserId", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,AppDefinitionId,CreatedById,CreatedDate,FormFactor,IsDeleted,LastModifiedById,LastModifiedDate,UserId,SystemModstamp
                      """
            entity = "USERAPPINFO"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "user_app_info_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)


class BulkUserRoleStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_role.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "user_roles_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CaseAccessForAccountOwner", StringType),
        Property("ContactAccessForAccountOwner", StringType),
        Property("DeveloperName", StringType),
        Property("ForecastUserId", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("MayForecastManagerShare", BooleanType),
        Property("OpportunityAccessForAccountOwner", StringType),
        Property("ParentRoleId", StringType),
        Property("PortalAccountId", StringType),
        Property("PortalAccountOwnerId", StringType),
        Property("PortalType", StringType),
        Property("RollupDescription", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,CaseAccessForAccountOwner,ContactAccessForAccountOwner,DeveloperName,ForecastUserId,LastModifiedById,LastModifiedDate,MayForecastManagerShare,
                          OpportunityAccessForAccountOwner,ParentRoleId,PortalAccountId,PortalAccountOwnerId,PortalType,RollupDescription,SystemModstamp
                      """
            entity = "USERROLE"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "user_roles_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)


class BulkApexClassStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_apexclass.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "apex_classes_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("ApiVersion", NumberType),
        Property("Body", StringType),
        Property("BodyCrc", IntegerType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("IsValid", BooleanType),
        Property("LengthWithoutComments", NumberType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("NamespacePrefix", StringType),
        Property("Status", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["ApiVersion", "BodyCrc", "LengthWithoutComments"]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,ApiVersion,Body,BodyCrc,CreatedById,CreatedDate,IsValid,LengthWithoutComments,LastModifiedById,LastModifiedDate,
                          NamespacePrefix,Status,SystemModstamp
                      """

            entity = "APEXCLASS"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "apex_classes_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkApexPageStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_apexpage.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "apex_pages_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("ApiVersion", NumberType),
        Property("ControllerKey", StringType),
        Property("ControllerType", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("IsAvailableInTouch", BooleanType),
        Property("IsConfirmationTokenRequired", BooleanType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("Markup", StringType),
        Property("MasterLabel", StringType),
        Property("NamespacePrefix", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["ApiVersion"]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,ApiVersion,ControllerKey,ControllerType,CreatedById,CreatedDate,Description,IsAvailableInTouch,
                          IsConfirmationTokenRequired,LastModifiedById,LastModifiedDate,Markup,MasterLabel,NamespacePrefix,SystemModstamp
                      """
            entity = "APEXPAGE"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "apex_pages_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkApexTriggerStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_apextrigger.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "apex_triggers_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("ApiVersion", NumberType),
        Property("Body", StringType),
        Property("BodyCrc", IntegerType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("IsValid", BooleanType),
        Property("LengthWithoutComments", NumberType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("NamespacePrefix", StringType),
        Property("Status", StringType),
        Property("TableEnumOrId", StringType),
        Property("UsageAfterDelete", BooleanType),
        Property("UsageAfterInsert", BooleanType),
        Property("UsageAfterUndelete", BooleanType),
        Property("UsageAfterUpdate", BooleanType),
        Property("UsageBeforeDelete", BooleanType),
        Property("UsageBeforeInsert", BooleanType),
        Property("UsageBeforeUpdate", BooleanType),
        Property("UsageIsBulk", BooleanType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["ApiVersion", "BodyCrc", "LengthWithoutComments"]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,ApiVersion,Body,BodyCrc,CreatedById,CreatedDate,IsValid,LengthWithoutComments,LastModifiedById,LastModifiedDate,NamespacePrefix,
                          Status,TableEnumOrId,UsageAfterDelete,UsageAfterInsert,UsageAfterUndelete,UsageAfterUpdate,UsageBeforeDelete,UsageBeforeInsert,
                          UsageBeforeUpdate,UsageIsBulk,SystemModstamp
                      """
            entity = "APEXTRIGGER"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "apex_triggers_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkCampaignMemberStatusStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_campaignmemberstatus.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "campaign_member_statuses_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("CampaignId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("HasResponded", BooleanType),
        Property("IsDefault", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("Label", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("SortOrder", NumberType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["SortOrder"]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,CampaignId,CreatedById,CreatedDate,HasResponded,IsDefault,IsDeleted,Label,LastModifiedById,LastModifiedDate,SortOrder,SystemModstamp
                      """
            entity = "CAMPAIGNMEMBERSTATUS"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "campaign_member_statuses_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkFiscalYearSettings(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_fiscalyearsettings.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "fiscal_year_settings_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "StartDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("Description", StringType),
        Property("EndDate", StringType),
        Property("IsStandardYear", BooleanType),
        Property("PeriodId", StringType),
        Property("PeriodLabelScheme", StringType),
        Property("PeriodPrefix", StringType),
        Property("QuarterLabelScheme", StringType),
        Property("QuarterPrefix", StringType),
        Property("StartDate", StringType),
        Property("WeekLabelScheme", StringType),
        Property("WeekStartDay", StringType),
        Property("YearType", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,Description,EndDate,IsStandardYear,PeriodId,PeriodLabelScheme,PeriodPrefix,QuarterLabelScheme,
                          QuarterPrefix,StartDate,WeekLabelScheme,WeekStartDay,YearType,SystemModstamp
                      """
            entity = "FISCALYEARSETTINGS"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "fiscal_year_settings_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)


class BulkOpportunityStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_opportunity.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "opportunities_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("AccountId", StringType),
        Property("Amount", NumberType),
        Property("CampaignId", StringType),
        Property("CloseDate", StringType),
        Property("ContactId", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("Description", StringType),
        Property("ExpectedRevenue", NumberType),
        Property("Fiscal", StringType),
        Property("FiscalQuarter", IntegerType),
        Property("FiscalYear", IntegerType),
        Property("ForecastCategory", StringType),
        Property("ForecastCategoryName", StringType),
        Property("HasOpenActivity", BooleanType),
        Property("HasOpportunityLineItem", BooleanType),
        Property("HasOverdueTask", BooleanType),
        Property("IsClosed", BooleanType),
        Property("IsDeleted", BooleanType),
        Property("IsPrivate", BooleanType),
        Property("IsWon", BooleanType),
        Property("LastActivityDate", StringType),
        Property("LastAmountChangedHistoryId", StringType),
        Property("LastCloseDateChangedHistoryId", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastStageChangeDate", StringType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("LeadSource", StringType),
        Property("NextStep", StringType),
        Property("OwnerId", StringType),
        Property("Pricebook2Id", StringType),
        Property("Probability", NumberType),
        Property("PushCount", IntegerType),
        Property("StageName", StringType),
        Property("TotalOpportunityQuantity", StringType),
        Property("Type", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = [
            "Amount",
            "ExpectedRevenue",
            "FiscalQuarter",
            "FiscalYear",
            "Probability",
            "PushCount",
            "TotalOpportunityQuantity",
        ]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,AccountId,Amount,CampaignId,CloseDate,ContactId,CreatedById,CreatedDate,
                          Description,ExpectedRevenue,Fiscal,FiscalQuarter,FiscalYear,ForecastCategory,ForecastCategoryName,HasOpenActivity,
                          HasOpportunityLineItem,HasOverdueTask,IsClosed,IsDeleted,IsPrivate,IsWon,LastActivityDate,LastAmountChangedHistoryId,
                          LastCloseDateChangedHistoryId,LastReferencedDate,LastStageChangeDate,LastViewedDate,LastModifiedById,LastModifiedDate,LeadSource,
                          NextStep,OwnerId,Pricebook2Id,Probability,PushCount,StageName,TotalOpportunityQuantity,Type,SystemModstamp
                      """
            entity = "OPPORTUNITY"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "opportunities_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkOrganizationStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_organization.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "organizations_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("Division", StringType),
        Property("Street", StringType),
        Property("City", StringType),
        Property("State", StringType),
        Property("PostalCode", StringType),
        Property("Country", StringType),
        Property("Latitude", StringType),
        Property("Longitude", StringType),
        Property("GeocodeAccuracy", StringType),
        Property("Phone", StringType),
        Property("Fax", StringType),
        Property("PrimaryContact", StringType),
        Property("DefaultLocaleSidKey", StringType),
        Property("TimeZoneSidKey", StringType),
        Property("LanguageLocaleKey", StringType),
        Property("ReceivesInfoEmails", BooleanType),
        Property("ReceivesAdminInfoEmails", BooleanType),
        Property("PreferencesRequireOpportunityProducts", BooleanType),
        Property("PreferencesConsentManagementEnabled", BooleanType),
        Property("PreferencesAutoSelectIndividualOnMerge", BooleanType),
        Property("PreferencesLightningLoginEnabled", BooleanType),
        Property("PreferencesOnlyLLPermUserAllowed", BooleanType),
        Property("FiscalYearStartMonth", IntegerType),
        Property("UsesStartDateAsFiscalYearName", BooleanType),
        Property("DefaultAccountAccess", StringType),
        Property("DefaultContactAccess", StringType),
        Property("DefaultOpportunityAccess", StringType),
        Property("DefaultLeadAccess", StringType),
        Property("DefaultCaseAccess", StringType),
        Property("DefaultCalendarAccess", StringType),
        Property("DefaultPricebookAccess", StringType),
        Property("DefaultCampaignAccess", StringType),
        Property("SystemModstamp", StringType),
        Property("ComplianceBccEmail", StringType),
        Property("UiSkin", StringType),
        Property("SignupCountryIsoCode", StringType),
        Property("TrialExpirationDate", StringType),
        Property("NumKnowledgeService", IntegerType),
        Property("OrganizationType", StringType),
        Property("NamespacePrefix", StringType),
        Property("InstanceName", StringType),
        Property("IsSandbox", BooleanType),
        Property("WebToCaseDefaultOrigin", StringType),
        Property("MonthlyPageViewsUsed", IntegerType),
        Property("MonthlyPageViewsEntitlement", IntegerType),
        Property("IsReadOnly", BooleanType),
        Property("CreatedDate", StringType),
        Property("CreatedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("PreferencesTransactionSecurityPolicy", BooleanType),
        Property("PreferencesTerminateOldestSession", BooleanType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = [
            "FiscalYearStartMonth",
            "NumKnowledgeService",
            "MonthlyPageViewsUsed",
            "MonthlyPageViewsEntitlement",
        ]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,Division,Street,City,State,PostalCode,Country,Latitude,Longitude,GeocodeAccuracy,Phone,Fax,
                          PrimaryContact,DefaultLocaleSidKey,TimeZoneSidKey,LanguageLocaleKey,ReceivesInfoEmails,
                          ReceivesAdminInfoEmails,PreferencesRequireOpportunityProducts,PreferencesConsentManagementEnabled,
                          PreferencesAutoSelectIndividualOnMerge,PreferencesLightningLoginEnabled,PreferencesOnlyLLPermUserAllowed,
                          FiscalYearStartMonth,UsesStartDateAsFiscalYearName,DefaultAccountAccess,DefaultContactAccess,
                          DefaultOpportunityAccess,DefaultLeadAccess,DefaultCaseAccess,DefaultCalendarAccess,DefaultPricebookAccess,
                          DefaultCampaignAccess,SystemModstamp,ComplianceBccEmail,UiSkin,SignupCountryIsoCode,TrialExpirationDate,
                          NumKnowledgeService,OrganizationType,NamespacePrefix,InstanceName,IsSandbox,WebToCaseDefaultOrigin,
                          MonthlyPageViewsUsed,MonthlyPageViewsEntitlement,IsReadOnly,CreatedDate,CreatedById,LastModifiedDate,
                          PreferencesTransactionSecurityPolicy,LastModifiedById
                      """
            entity = "ORGANIZATION"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "organizations_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkServiceSetupProvisioningStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_servicesetupprovisioning.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "service_setup_provisionings_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("IsDeleted", BooleanType),
        Property("JobName", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("Status", StringType),
        Property("TaskContext", StringType),
        Property("TaskName", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,CreatedById,CreatedDate,IsDeleted,JobName,LastModifiedById,LastModifiedDate,Status,TaskContext,TaskName,SystemModstamp
                      """
            entity = "SERVICESETUPPROVISIONING"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "service_setup_provisionings_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)


class BulkBusinessHoursStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_businesshours.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "business_hours_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("FridayEndTime", StringType),
        Property("FridayStartTime", StringType),
        Property("IsActive", BooleanType),
        Property("IsDefault", BooleanType),
        Property("LastViewedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("MondayEndTime", StringType),
        Property("MondayStartTime", StringType),
        Property("SaturdayEndTime", StringType),
        Property("SaturdayStartTime", StringType),
        Property("SundayEndTime", StringType),
        Property("SundayStartTime", StringType),
        Property("ThursdayEndTime", StringType),
        Property("ThursdayStartTime", StringType),
        Property("TimeZoneSidKey", StringType),
        Property("TuesdayEndTime", StringType),
        Property("TuesdayStartTime", StringType),
        Property("WednesdayEndTime", StringType),
        Property("WednesdayStartTime", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Name,CreatedById,CreatedDate,FridayEndTime,FridayStartTime,IsActive,IsDefault,LastViewedDate,LastModifiedById,LastModifiedDate,MondayEndTime,
                          MondayStartTime,SaturdayEndTime,SaturdayStartTime,SundayEndTime,SundayStartTime,ThursdayEndTime,ThursdayStartTime,TimeZoneSidKey,TuesdayEndTime,
                          TuesdayStartTime,WednesdayEndTime,WednesdayStartTime,SystemModstamp
                      """

            entity = "BUSINESSHOURS"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "business_hours_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)


class BulkUserStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_user.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "users_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Name", StringType),
        Property("AboutMe", StringType),
        Property("AccountId", StringType),
        Property("Alias", StringType),
        Property("BadgeText", StringType),
        Property("BannerPhotoUrl", StringType),
        Property("CallCenterId", StringType),
        Property("City", StringType),
        Property("CommunityNickname", StringType),
        Property("CompanyName", StringType),
        Property("ContactId", StringType),
        Property("Country", StringType),
        Property("CreatedById", StringType),
        Property("CreatedDate", StringType),
        Property("DefaultGroupNotificationFrequency", StringType),
        Property("DelegatedApproverId", StringType),
        Property("Department", StringType),
        Property("DigestFrequency", StringType),
        Property("Division", StringType),
        Property("Email", StringType),
        Property("EmailEncodingKey", StringType),
        Property("EmailPreferencesAutoBcc", BooleanType),
        Property("EmailPreferencesAutoBccStayInTouch", BooleanType),
        Property("EmailPreferencesStayInTouchReminder", BooleanType),
        Property("EmployeeNumber", StringType),
        Property("Extension", StringType),
        Property("Fax", StringType),
        Property("FederationIdentifier", StringType),
        Property("FirstName", StringType),
        Property("ForecastEnabled", BooleanType),
        Property("FullPhotoUrl", StringType),
        Property("GeocodeAccuracy", StringType),
        Property("IndividualId", StringType),
        Property("IsActive", BooleanType),
        Property("IsProfilePhotoActive", BooleanType),
        Property("IsExtIndicatorVisible", BooleanType),
        Property("JigsawImportLimitOverride", IntegerType),
        Property("LanguageLocaleKey", StringType),
        Property("LastLoginDate", StringType),
        Property("LastName", StringType),
        Property("LastReferencedDate", StringType),
        Property("LastViewedDate", StringType),
        Property("Latitude", StringType),
        Property("LocaleSidKey", StringType),
        Property("Longitude", StringType),
        Property("LastPasswordChangeDate", StringType),
        Property("LastModifiedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("ManagerId", StringType),
        Property("MediumBannerPhotoUrl", StringType),
        Property("MediumPhotoUrl", StringType),
        Property("MobilePhone", StringType),
        Property("NumberOfFailedLogins", IntegerType),
        Property("OfflinePdaTrialExpirationDate", StringType),
        Property("OfflineTrialExpirationDate", StringType),
        Property("OutOfOfficeMessage", StringType),
        Property("Phone", StringType),
        Property("PostalCode", StringType),
        Property("ProfileId", StringType),
        Property("ReceivesAdminInfoEmails", BooleanType),
        Property("ReceivesInfoEmails", BooleanType),
        Property("SenderEmail", StringType),
        Property("SenderName", StringType),
        Property("Signature", StringType),
        Property("SmallBannerPhotoUrl", StringType),
        Property("SmallPhotoUrl", StringType),
        Property("State", StringType),
        Property("StayInTouchNote", StringType),
        Property("StayInTouchSignature", StringType),
        Property("StayInTouchSubject", StringType),
        Property("Street", StringType),
        Property("TimeZoneSidKey", StringType),
        Property("Title", StringType),
        Property("Username", StringType),
        Property("UserPermissionsCallCenterAutoLogin", BooleanType),
        Property("UserPermissionsInteractionUser", BooleanType),
        Property("UserPermissionsJigsawProspectingUser", BooleanType),
        Property("UserPermissionsKnowledgeUser", BooleanType),
        Property("UserPermissionsMarketingUser", BooleanType),
        Property("UserPermissionsOfflineUser", BooleanType),
        Property("UserPermissionsSFContentUser", BooleanType),
        Property("UserPermissionsSiteforceContributorUser", BooleanType),
        Property("UserPermissionsSiteforcePublisherUser", BooleanType),
        Property("UserPermissionsSupportUser", BooleanType),
        Property("UserPermissionsWorkDotComUserFeature", BooleanType),
        Property("UserPreferencesActivityRemindersPopup", BooleanType),
        Property("UserPreferencesApexPagesDeveloperMode", BooleanType),
        Property("UserPreferencesCacheDiagnostics", BooleanType),
        Property("UserPreferencesContentEmailAsAndWhen", BooleanType),
        Property("UserPreferencesContentNoEmail", BooleanType),
        Property("UserPreferencesCreateLEXAppsWTShown", BooleanType),
        Property("UserPreferencesEnableAutoSubForFeeds", BooleanType),
        Property("UserPreferencesDisableAllFeedsEmail", BooleanType),
        Property("UserPreferencesDisableBookmarkEmail", BooleanType),
        Property("UserPreferencesDisableChangeCommentEmail", BooleanType),
        Property("UserPreferencesDisableEndorsementEmail", BooleanType),
        Property("UserPreferencesDisableFileShareNotificationsForApi", BooleanType),
        Property("UserPreferencesDisableFollowersEmail", BooleanType),
        Property("UserPreferencesDisableLaterCommentEmail", BooleanType),
        Property("UserPreferencesDisableLikeEmail", BooleanType),
        Property("UserPreferencesDisableMentionsPostEmail", BooleanType),
        Property("UserPreferencesDisableProfilePostEmail", BooleanType),
        Property("UserPreferencesDisableSharePostEmail", BooleanType),
        Property("UserPreferencesDisCommentAfterLikeEmail", BooleanType),
        Property("UserPreferencesDisMentionsCommentEmail", BooleanType),
        Property("UserPreferencesDisableMessageEmail", BooleanType),
        Property("UserPreferencesDisProfPostCommentEmail", BooleanType),
        Property("UserPreferencesEventRemindersCheckboxDefault", BooleanType),
        Property("UserPreferencesExcludeMailAppAttachments", BooleanType),
        Property("UserPreferencesFavoritesShowTopFavorites", BooleanType),
        Property("UserPreferencesFavoritesWTShown", BooleanType),
        Property("UserPreferencesGlobalNavBarWTShown", BooleanType),
        Property("UserPreferencesGlobalNavGridMenuWTShown", BooleanType),
        Property("UserPreferencesHasCelebrationBadge", BooleanType),
        Property("UserPreferencesHasSentWarningEmail", BooleanType),
        Property("UserPreferencesHasSentWarningEmail238", BooleanType),
        Property("UserPreferencesHasSentWarningEmail240", BooleanType),
        Property("UserPreferencesHideBiggerPhotoCallout", BooleanType),
        Property("UserPreferencesHideChatterOnboardingSplash", BooleanType),
        Property("UserPreferencesHideCSNDesktopTask", BooleanType),
        Property("UserPreferencesHideCSNGetChatterMobileTask", BooleanType),
        Property("UserPreferencesHideEndUserOnboardingAssistantModal", BooleanType),
        Property("UserPreferencesHideLightningMigrationModal", BooleanType),
        Property("UserPreferencesHideSecondChatterOnboardingSplash", BooleanType),
        Property("UserPreferencesHideS1BrowserUI", BooleanType),
        Property("UserPreferencesHideSfxWelcomeMat", BooleanType),
        Property("UserPreferencesJigsawListUser", BooleanType),
        Property("UserPreferencesLightningExperiencePreferred", BooleanType),
        Property("UserPreferencesNativeEmailClient", BooleanType),
        Property("UserPreferencesNewLightningReportRunPageEnabled", BooleanType),
        Property("UserPreferencesPathAssistantCollapsed", BooleanType),
        Property("UserPreferencesPreviewCustomTheme", BooleanType),
        Property("UserPreferencesPreviewLightning", BooleanType),
        Property("UserPreferencesRecordHomeReservedWTShown", BooleanType),
        Property("UserPreferencesRecordHomeSectionCollapseWTShown", BooleanType),
        Property("UserPreferencesReceiveNoNotificationsAsApprover", BooleanType),
        Property("UserPreferencesReceiveNotificationsAsDelegatedApprover", BooleanType),
        Property("UserPreferencesReminderSoundOff", BooleanType),
        Property("UserPreferencesReverseOpenActivitiesView", BooleanType),
        Property("UserPreferencesShowCityToExternalUsers", BooleanType),
        Property("UserPreferencesShowCityToGuestUsers", BooleanType),
        Property("UserPreferencesShowCountryToExternalUsers", BooleanType),
        Property("UserPreferencesShowCountryToGuestUsers", BooleanType),
        Property("UserPreferencesShowEmailToExternalUsers", BooleanType),
        Property("UserPreferencesShowEmailToGuestUsers", BooleanType),
        Property("UserPreferencesShowFaxToExternalUsers", BooleanType),
        Property("UserPreferencesShowFaxToGuestUsers", BooleanType),
        Property("UserPreferencesShowForecastingChangeSignals", BooleanType),
        Property("UserPreferencesShowManagerToExternalUsers", BooleanType),
        Property("UserPreferencesShowManagerToGuestUsers", BooleanType),
        Property("UserPreferencesShowMobilePhoneToExternalUsers", BooleanType),
        Property("UserPreferencesShowMobilePhoneToGuestUsers", BooleanType),
        Property("UserPreferencesShowPostalCodeToExternalUsers", BooleanType),
        Property("UserPreferencesShowPostalCodeToGuestUsers", BooleanType),
        Property("UserPreferencesShowProfilePicToGuestUsers", BooleanType),
        Property("UserPreferencesShowStateToExternalUsers", BooleanType),
        Property("UserPreferencesShowStateToGuestUsers", BooleanType),
        Property("UserPreferencesShowStreetAddressToExternalUsers", BooleanType),
        Property("UserPreferencesShowStreetAddressToGuestUsers", BooleanType),
        Property("UserPreferencesShowTitleToExternalUsers", BooleanType),
        Property("UserPreferencesShowTitleToGuestUsers", BooleanType),
        Property("UserPreferencesShowTerritoryTimeZoneShifts", BooleanType),
        Property("UserPreferencesShowWorkPhoneToExternalUsers", BooleanType),
        Property("UserPreferencesShowWorkPhoneToGuestUsers", BooleanType),
        Property("UserPreferencesSortFeedByComment", BooleanType),
        Property("UserPreferencesSRHOverrideActivities", BooleanType),
        Property("UserPreferencesSuppressEventSFXReminders", BooleanType),
        Property("UserPreferencesSuppressTaskSFXReminders", BooleanType),
        Property("UserPreferencesTaskRemindersCheckboxDefault", BooleanType),
        Property("UserPreferencesUserDebugModePref", BooleanType),
        Property("UserRoleId", StringType),
        Property("UserType", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def convert_to_numeric(self, value):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        # List of column names with numeric or integer values
        numeric_columns = ["JigsawImportLimitOverride", "NumberOfFailedLogins"]
        for column in numeric_columns:
            if column in row:
                row[column] = self.convert_to_numeric(row[column])
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]
            columns = """
                          Id,Name,AboutMe,AccountId,Alias,BadgeText,BannerPhotoUrl,CallCenterId,City,CommunityNickname,CompanyName,
                          ContactId,Country,CreatedById,CreatedDate,DefaultGroupNotificationFrequency,DelegatedApproverId,Department,DigestFrequency,
                          Division,Email,EmailEncodingKey,EmailPreferencesAutoBcc,EmailPreferencesAutoBccStayInTouch,EmailPreferencesStayInTouchReminder,
                          EmployeeNumber,Extension,Fax,FederationIdentifier,FirstName,ForecastEnabled,FullPhotoUrl,GeocodeAccuracy,IndividualId,IsActive,IsProfilePhotoActive,
                          IsExtIndicatorVisible,JigsawImportLimitOverride,LanguageLocaleKey,LastLoginDate,LastName,LastReferencedDate,LastViewedDate,Latitude,LocaleSidKey,
                          Longitude,LastPasswordChangeDate,LastModifiedById,LastModifiedDate,ManagerId,MediumBannerPhotoUrl,MediumPhotoUrl,MobilePhone,NumberOfFailedLogins,
                          OfflinePdaTrialExpirationDate,OfflineTrialExpirationDate,OutOfOfficeMessage,Phone,PostalCode,ProfileId,ReceivesAdminInfoEmails,ReceivesInfoEmails,
                          SenderEmail,SenderName,Signature,SmallBannerPhotoUrl,SmallPhotoUrl,State,StayInTouchNote,StayInTouchSignature,StayInTouchSubject,Street,TimeZoneSidKey,
                          Title,Username,UserPermissionsCallCenterAutoLogin,UserPermissionsInteractionUser,UserPermissionsJigsawProspectingUser,UserPermissionsKnowledgeUser,
                          UserPermissionsMarketingUser,UserPermissionsOfflineUser,UserPermissionsSFContentUser,UserPermissionsSiteforceContributorUser,
                          UserPermissionsSiteforcePublisherUser,UserPermissionsSupportUser,UserPermissionsWorkDotComUserFeature,UserPreferencesActivityRemindersPopup,
                          UserPreferencesApexPagesDeveloperMode,UserPreferencesCacheDiagnostics,UserPreferencesContentEmailAsAndWhen,UserPreferencesContentNoEmail,
                          UserPreferencesCreateLEXAppsWTShown,UserPreferencesEnableAutoSubForFeeds,UserPreferencesDisableAllFeedsEmail,UserPreferencesDisableBookmarkEmail,
                          UserPreferencesDisableChangeCommentEmail,UserPreferencesDisableEndorsementEmail,UserPreferencesDisableFileShareNotificationsForApi,
                          UserPreferencesDisableFollowersEmail,UserPreferencesDisableLaterCommentEmail,UserPreferencesDisableLikeEmail,UserPreferencesDisableMentionsPostEmail,
                          UserPreferencesDisableProfilePostEmail,UserPreferencesDisableSharePostEmail,UserPreferencesDisCommentAfterLikeEmail,UserPreferencesDisMentionsCommentEmail,
                          UserPreferencesDisableMessageEmail,UserPreferencesDisProfPostCommentEmail,UserPreferencesEventRemindersCheckboxDefault,UserPreferencesExcludeMailAppAttachments,
                          UserPreferencesFavoritesShowTopFavorites,UserPreferencesFavoritesWTShown,UserPreferencesGlobalNavBarWTShown,UserPreferencesGlobalNavGridMenuWTShown,
                          UserPreferencesHasCelebrationBadge,UserPreferencesHasSentWarningEmail,UserPreferencesHasSentWarningEmail238,UserPreferencesHasSentWarningEmail240,
                          UserPreferencesHideBiggerPhotoCallout,UserPreferencesHideChatterOnboardingSplash,UserPreferencesHideCSNDesktopTask,UserPreferencesHideCSNGetChatterMobileTask,
                          UserPreferencesHideEndUserOnboardingAssistantModal,UserPreferencesHideLightningMigrationModal,
                          UserPreferencesHideSecondChatterOnboardingSplash,UserPreferencesHideS1BrowserUI,UserPreferencesHideSfxWelcomeMat,UserPreferencesJigsawListUser,
                          UserPreferencesLightningExperiencePreferred,UserPreferencesNativeEmailClient,UserPreferencesNewLightningReportRunPageEnabled,UserPreferencesPathAssistantCollapsed,
                          UserPreferencesReceiveNoNotificationsAsApprover,UserPreferencesPreviewCustomTheme,UserPreferencesPreviewLightning,UserPreferencesRecordHomeReservedWTShown,
                          UserPreferencesRecordHomeSectionCollapseWTShown,UserPreferencesReverseOpenActivitiesView,UserPreferencesReceiveNotificationsAsDelegatedApprover,
                          UserPreferencesReminderSoundOff,UserPreferencesShowCityToExternalUsers,UserPreferencesShowCityToGuestUsers,UserPreferencesShowCountryToExternalUsers,
                          UserPreferencesShowCountryToGuestUsers,UserPreferencesShowEmailToExternalUsers,UserPreferencesShowEmailToGuestUsers,UserPreferencesShowFaxToExternalUsers,
                          UserPreferencesShowFaxToGuestUsers,UserPreferencesShowForecastingChangeSignals,UserPreferencesShowManagerToExternalUsers,UserPreferencesShowManagerToGuestUsers,
                          UserPreferencesShowMobilePhoneToExternalUsers,UserPreferencesShowMobilePhoneToGuestUsers,UserPreferencesShowPostalCodeToExternalUsers,
                          UserPreferencesShowPostalCodeToGuestUsers,UserPreferencesShowProfilePicToGuestUsers,UserPreferencesShowStateToExternalUsers,
                          UserPreferencesShowStateToGuestUsers,UserPreferencesShowStreetAddressToExternalUsers,UserPreferencesShowStreetAddressToGuestUsers,
                          UserPreferencesShowTitleToExternalUsers,UserPreferencesShowTitleToGuestUsers,UserPreferencesShowTerritoryTimeZoneShifts,
                          UserPreferencesShowWorkPhoneToExternalUsers,UserPreferencesShowWorkPhoneToGuestUsers,UserPreferencesSortFeedByComment,UserPreferencesSRHOverrideActivities,
                          UserPreferencesSuppressEventSFXReminders,UserPreferencesSuppressTaskSFXReminders,UserPreferencesTaskRemindersCheckboxDefault,
                          UserPreferencesUserDebugModePref,UserRoleId,UserType,SystemModstamp
                      """
            entity = "USER"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "users_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield self.post_process(record, context)
        except Exception as e:
            pass
            self.logger.info(e)


class BulkProfileStream(SalesforceStream):

    """
    https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_businesshours.htm
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "profiles_bulk"
    path = ""
    primary_keys = ["Id"]
    replication_key = "LastModifiedDate"
    replication_method = "INCREMENTAL"

    schema = PropertiesList(
        Property("Id", StringType),
        Property("Description", StringType),
        Property("LastReferencedDate", StringType),
        Property("PermissionsEmailSingle", BooleanType),
        Property("PermissionsEmailMass", BooleanType),
        Property("PermissionsEditTask", BooleanType),
        Property("PermissionsEditEvent", BooleanType),
        Property("PermissionsExportReport", BooleanType),
        Property("PermissionsImportPersonal", BooleanType),
        Property("PermissionsDataExport", BooleanType),
        Property("PermissionsManageUsers", BooleanType),
        Property("PermissionsEditPublicFilters", BooleanType),
        Property("PermissionsEditPublicTemplates", BooleanType),
        Property("PermissionsModifyAllData", BooleanType),
        Property("PermissionsEditBillingInfo", BooleanType),
        Property("PermissionsManageCases", BooleanType),
        Property("PermissionsMassInlineEdit", BooleanType),
        Property("PermissionsEditKnowledge", BooleanType),
        Property("PermissionsManageKnowledge", BooleanType),
        Property("PermissionsManageSolutions", BooleanType),
        Property("PermissionsCustomizeApplication", BooleanType),
        Property("PermissionsEditReadonlyFields", BooleanType),
        Property("PermissionsRunReports", BooleanType),
        Property("PermissionsViewSetup", BooleanType),
        Property("PermissionsTransferAnyEntity", BooleanType),
        Property("PermissionsNewReportBuilder", BooleanType),
        Property("PermissionsActivateContract", BooleanType),
        Property("PermissionsActivateOrder", BooleanType),
        Property("PermissionsImportLeads", BooleanType),
        Property("PermissionsManageLeads", BooleanType),
        Property("PermissionsTransferAnyLead", BooleanType),
        Property("PermissionsViewAllData", BooleanType),
        Property("PermissionsEditPublicDocuments", BooleanType),
        Property("PermissionsViewEncryptedData", BooleanType),
        Property("PermissionsEditBrandTemplates", BooleanType),
        Property("PermissionsEditHtmlTemplates", BooleanType),
        Property("PermissionsChatterInternalUser", BooleanType),
        Property("PermissionsManageEncryptionKeys", BooleanType),
        Property("PermissionsDeleteActivatedContract", BooleanType),
        Property("PermissionsChatterInviteExternalUsers", BooleanType),
        Property("PermissionsSendSitRequests", BooleanType),
        Property("PermissionsApiUserOnly", BooleanType),
        Property("PermissionsManageRemoteAccess", BooleanType),
        Property("PermissionsCanUseNewDashboardBuilder", BooleanType),
        Property("PermissionsManageCategories", BooleanType),
        Property("PermissionsConvertLeads", BooleanType),
        Property("PermissionsPasswordNeverExpires", BooleanType),
        Property("PermissionsUseTeamReassignWizards", BooleanType),
        Property("PermissionsEditActivatedOrders", BooleanType),
        Property("PermissionsInstallMultiforce", BooleanType),
        Property("PermissionsPublishMultiforce", BooleanType),
        Property("PermissionsChatterOwnGroups", BooleanType),
        Property("PermissionsEditOppLineItemUnitPrice", BooleanType),
        Property("PermissionsCreateMultiforce", BooleanType),
        Property("PermissionsBulkApiHardDelete", BooleanType),
        Property("PermissionsSolutionImport", BooleanType),
        Property("PermissionsManageCallCenters", BooleanType),
        Property("PermissionsManageSynonyms", BooleanType),
        Property("PermissionsViewContent", BooleanType),
        Property("PermissionsManageEmailClientConfig", BooleanType),
        Property("PermissionsEnableNotifications", BooleanType),
        Property("PermissionsManageDataIntegrations", BooleanType),
        Property("PermissionsDistributeFromPersWksp", BooleanType),
        Property("PermissionsViewDataCategories", BooleanType),
        Property("PermissionsManageDataCategories", BooleanType),
        Property("PermissionsAuthorApex", BooleanType),
        Property("PermissionsManageMobile", BooleanType),
        Property("PermissionsApiEnabled", BooleanType),
        Property("PermissionsManageCustomReportTypes", BooleanType),
        Property("PermissionsEditCaseComments", BooleanType),
        Property("PermissionsTransferAnyCase", BooleanType),
        Property("PermissionsContentAdministrator", BooleanType),
        Property("PermissionsCreateWorkspaces", BooleanType),
        Property("PermissionsManageContentPermissions", BooleanType),
        Property("PermissionsManageContentProperties", BooleanType),
        Property("PermissionsManageContentTypes", BooleanType),
        Property("PermissionsManageExchangeConfig", BooleanType),
        Property("PermissionsManageAnalyticSnapshots", BooleanType),
        Property("PermissionsScheduleReports", BooleanType),
        Property("PermissionsManageBusinessHourHolidays", BooleanType),
        Property("PermissionsManageEntitlements", BooleanType),
        Property("PermissionsManageDynamicDashboards", BooleanType),
        Property("PermissionsCustomSidebarOnAllPages", BooleanType),
        Property("PermissionsManageInteraction", BooleanType),
        Property("PermissionsViewMyTeamsDashboards", BooleanType),
        Property("PermissionsModerateChatter", BooleanType),
        Property("PermissionsResetPasswords", BooleanType),
        Property("PermissionsFlowUFLRequired", BooleanType),
        Property("PermissionsCanInsertFeedSystemFields", BooleanType),
        Property("PermissionsActivitiesAccess", BooleanType),
        Property("PermissionsManageKnowledgeImportExport", BooleanType),
        Property("PermissionsEmailTemplateManagement", BooleanType),
        Property("PermissionsEmailAdministration", BooleanType),
        Property("PermissionsManageChatterMessages", BooleanType),
        Property("PermissionsAllowEmailIC", BooleanType),
        Property("PermissionsChatterFileLink", BooleanType),
        Property("PermissionsForceTwoFactor", BooleanType),
        Property("PermissionsViewEventLogFiles", BooleanType),
        Property("PermissionsManageNetworks", BooleanType),
        Property("PermissionsManageAuthProviders", BooleanType),
        Property("PermissionsRunFlow", BooleanType),
        Property("PermissionsCreateCustomizeDashboards", BooleanType),
        Property("PermissionsCreateDashboardFolders", BooleanType),
        Property("PermissionsViewPublicDashboards", BooleanType),
        Property("PermissionsManageDashbdsInPubFolders", BooleanType),
        Property("PermissionsCreateCustomizeReports", BooleanType),
        Property("PermissionsCreateReportFolders", BooleanType),
        Property("PermissionsViewPublicReports", BooleanType),
        Property("PermissionsManageReportsInPubFolders", BooleanType),
        Property("PermissionsEditMyDashboards", BooleanType),
        Property("PermissionsEditMyReports", BooleanType),
        Property("PermissionsViewAllUsers", BooleanType),
        Property("PermissionsAllowUniversalSearch", BooleanType),
        Property("PermissionsConnectOrgToEnvironmentHub", BooleanType),
        Property("PermissionsWorkCalibrationUser", BooleanType),
        Property("PermissionsCreateCustomizeFilters", BooleanType),
        Property("PermissionsWorkDotComUserPerm", BooleanType),
        Property("PermissionsContentHubUser", BooleanType),
        Property("PermissionsGovernNetworks", BooleanType),
        Property("PermissionsSalesConsole", BooleanType),
        Property("PermissionsTwoFactorApi", BooleanType),
        Property("PermissionsDeleteTopics", BooleanType),
        Property("PermissionsEditTopics", BooleanType),
        Property("PermissionsCreateTopics", BooleanType),
        Property("PermissionsAssignTopics", BooleanType),
        Property("PermissionsIdentityEnabled", BooleanType),
        Property("PermissionsIdentityConnect", BooleanType),
        Property("PermissionsAllowViewKnowledge", BooleanType),
        Property("PermissionsContentWorkspaces", BooleanType),
        Property("PermissionsManageSearchPromotionRules", BooleanType),
        Property("PermissionsCustomMobileAppsAccess", BooleanType),
        Property("PermissionsViewHelpLink", BooleanType),
        Property("PermissionsManageProfilesPermissionsets", BooleanType),
        Property("PermissionsAssignPermissionSets", BooleanType),
        Property("PermissionsManageRoles", BooleanType),
        Property("PermissionsManageIpAddresses", BooleanType),
        Property("PermissionsManageSharing", BooleanType),
        Property("PermissionsManageInternalUsers", BooleanType),
        Property("PermissionsManagePasswordPolicies", BooleanType),
        Property("PermissionsManageLoginAccessPolicies", BooleanType),
        Property("PermissionsViewPlatformEvents", BooleanType),
        Property("PermissionsManageCustomPermissions", BooleanType),
        Property("PermissionsCanVerifyComment", BooleanType),
        Property("PermissionsManageUnlistedGroups", BooleanType),
        Property("PermissionsStdAutomaticActivityCapture", BooleanType),
        Property("PermissionsInsightsAppDashboardEditor", BooleanType),
        Property("PermissionsManageTwoFactor", BooleanType),
        Property("PermissionsInsightsAppUser", BooleanType),
        Property("PermissionsInsightsAppAdmin", BooleanType),
        Property("PermissionsInsightsAppEltEditor", BooleanType),
        Property("PermissionsInsightsAppUploadUser", BooleanType),
        Property("PermissionsInsightsCreateApplication", BooleanType),
        Property("PermissionsLightningExperienceUser", BooleanType),
        Property("PermissionsViewDataLeakageEvents", BooleanType),
        Property("PermissionsConfigCustomRecs", BooleanType),
        Property("PermissionsSubmitMacrosAllowed", BooleanType),
        Property("PermissionsBulkMacrosAllowed", BooleanType),
        Property("PermissionsShareInternalArticles", BooleanType),
        Property("PermissionsManageSessionPermissionSets", BooleanType),
        Property("PermissionsManageTemplatedApp", BooleanType),
        Property("PermissionsUseTemplatedApp", BooleanType),
        Property("PermissionsSendAnnouncementEmails", BooleanType),
        Property("PermissionsChatterEditOwnPost", BooleanType),
        Property("PermissionsChatterEditOwnRecordPost", BooleanType),
        Property("PermissionsWaveTabularDownload", BooleanType),
        Property("PermissionsAutomaticActivityCapture", BooleanType),
        Property("PermissionsImportCustomObjects", BooleanType),
        Property("PermissionsDelegatedTwoFactor", BooleanType),
        Property("PermissionsChatterComposeUiCodesnippet", BooleanType),
        Property("PermissionsSelectFilesFromSalesforce", BooleanType),
        Property("PermissionsModerateNetworkUsers", BooleanType),
        Property("PermissionsMergeTopics", BooleanType),
        Property("PermissionsSubscribeToLightningReports", BooleanType),
        Property("PermissionsManagePvtRptsAndDashbds", BooleanType),
        Property("PermissionsAllowLightningLogin", BooleanType),
        Property("PermissionsCampaignInfluence2", BooleanType),
        Property("PermissionsViewDataAssessment", BooleanType),
        Property("PermissionsRemoveDirectMessageMembers", BooleanType),
        Property("PermissionsCanApproveFeedPost", BooleanType),
        Property("PermissionsAddDirectMessageMembers", BooleanType),
        Property("PermissionsAllowViewEditConvertedLeads", BooleanType),
        Property("PermissionsShowCompanyNameAsUserBadge", BooleanType),
        Property("PermissionsAccessCMC", BooleanType),
        Property("PermissionsViewHealthCheck", BooleanType),
        Property("PermissionsManageHealthCheck", BooleanType),
        Property("PermissionsPackaging2", BooleanType),
        Property("PermissionsManageCertificates", BooleanType),
        Property("PermissionsCreateReportInLightning", BooleanType),
        Property("PermissionsPreventClassicExperience", BooleanType),
        Property("PermissionsHideReadByList", BooleanType),
        Property("PermissionsListEmailSend", BooleanType),
        Property("PermissionsFeedPinning", BooleanType),
        Property("PermissionsChangeDashboardColors", BooleanType),
        Property("PermissionsManageRecommendationStrategies", BooleanType),
        Property("PermissionsManagePropositions", BooleanType),
        Property("PermissionsCloseConversations", BooleanType),
        Property("PermissionsSubscribeReportRolesGrps", BooleanType),
        Property("PermissionsSubscribeDashboardRolesGrps", BooleanType),
        Property("PermissionsUseWebLink", BooleanType),
        Property("PermissionsHasUnlimitedNBAExecutions", BooleanType),
        Property("PermissionsViewOnlyEmbeddedAppUser", BooleanType),
        Property("PermissionsViewAllActivities", BooleanType),
        Property("PermissionsSubscribeReportToOtherUsers", BooleanType),
        Property("PermissionsLightningConsoleAllowedForUser", BooleanType),
        Property("PermissionsSubscribeReportsRunAsUser", BooleanType),
        Property("PermissionsSubscribeToLightningDashboards", BooleanType),
        Property("PermissionsSubscribeDashboardToOtherUsers", BooleanType),
        Property("PermissionsCreateLtngTempInPub", BooleanType),
        Property("PermissionsAppointmentBookingUserAccess", BooleanType),
        Property("PermissionsTransactionalEmailSend", BooleanType),
        Property("PermissionsViewPrivateStaticResources", BooleanType),
        Property("PermissionsCreateLtngTempFolder", BooleanType),
        Property("PermissionsApexRestServices", BooleanType),
        Property("PermissionsConfigureLiveMessage", BooleanType),
        Property("PermissionsLiveMessageAgent", BooleanType),
        Property("PermissionsEnableCommunityAppLauncher", BooleanType),
        Property("PermissionsGiveRecognitionBadge", BooleanType),
        Property("PermissionsLightningSchedulerUserAccess", BooleanType),
        Property("PermissionsUseMySearch", BooleanType),
        Property("PermissionsLtngPromoReserved01UserPerm", BooleanType),
        Property("PermissionsManageSubscriptions", BooleanType),
        Property("PermissionsWaveManagePrivateAssetsUser", BooleanType),
        Property("PermissionsCanEditDataPrepRecipe", BooleanType),
        Property("PermissionsAddAnalyticsRemoteConnections", BooleanType),
        Property("PermissionsManageSurveys", BooleanType),
        Property("PermissionsUseAssistantDialog", BooleanType),
        Property("PermissionsUseQuerySuggestions", BooleanType),
        Property("PermissionsPackaging2PromoteVersion", BooleanType),
        Property("PermissionsRecordVisibilityAPI", BooleanType),
        Property("PermissionsViewRoles", BooleanType),
        Property("PermissionsCanManageMaps", BooleanType),
        Property("PermissionsLMOutboundMessagingUserPerm", BooleanType),
        Property("PermissionsModifyDataClassification", BooleanType),
        Property("PermissionsPrivacyDataAccess", BooleanType),
        Property("PermissionsQueryAllFiles", BooleanType),
        Property("PermissionsModifyMetadata", BooleanType),
        Property("PermissionsManageCMS", BooleanType),
        Property("PermissionsSandboxTestingInCommunityApp", BooleanType),
        Property("PermissionsCanEditPrompts", BooleanType),
        Property("PermissionsViewUserPII", BooleanType),
        Property("PermissionsManageHubConnections", BooleanType),
        Property("PermissionsB2BMarketingAnalyticsUser", BooleanType),
        Property("PermissionsTraceXdsQueries", BooleanType),
        Property("PermissionsViewSecurityCommandCenter", BooleanType),
        Property("PermissionsManageSecurityCommandCenter", BooleanType),
        Property("PermissionsViewAllCustomSettings", BooleanType),
        Property("PermissionsViewAllForeignKeyNames", BooleanType),
        Property("PermissionsAddWaveNotificationRecipients", BooleanType),
        Property("PermissionsHeadlessCMSAccess", BooleanType),
        Property("PermissionsLMEndMessagingSessionUserPerm", BooleanType),
        Property("PermissionsConsentApiUpdate", BooleanType),
        Property("PermissionsPaymentsAPIUser", BooleanType),
        Property("PermissionsAccessContentBuilder", BooleanType),
        Property("PermissionsAccountSwitcherUser", BooleanType),
        Property("PermissionsViewAnomalyEvents", BooleanType),
        Property("PermissionsManageC360AConnections", BooleanType),
        Property("PermissionsIsContactCenterAdmin", BooleanType),
        Property("PermissionsIsContactCenterAgent", BooleanType),
        Property("PermissionsManageReleaseUpdates", BooleanType),
        Property("PermissionsViewAllProfiles", BooleanType),
        Property("PermissionsSkipIdentityConfirmation", BooleanType),
        Property("PermissionsCanToggleCallRecordings", BooleanType),
        Property("PermissionsLearningManager", BooleanType),
        Property("PermissionsSendCustomNotifications", BooleanType),
        Property("PermissionsPackaging2Delete", BooleanType),
        Property("PermissionsUseOmnichannelInventoryAPIs", BooleanType),
        Property("PermissionsViewRestrictionAndScopingRules", BooleanType),
        Property("PermissionsFSCComprehensiveUserAccess", BooleanType),
        Property("PermissionsBotManageBots", BooleanType),
        Property("PermissionsBotManageBotsTrainingData", BooleanType),
        Property("PermissionsSchedulingLineAmbassador", BooleanType),
        Property("PermissionsSchedulingFacilityManager", BooleanType),
        Property("PermissionsOmnichannelInventorySync", BooleanType),
        Property("PermissionsManageLearningReporting", BooleanType),
        Property("PermissionsIsContactCenterSupervisor", BooleanType),
        Property("PermissionsIsotopeCToCUser", BooleanType),
        Property("PermissionsCanAccessCE", BooleanType),
        Property("PermissionsUseAddOrderItemSummaryAPIs", BooleanType),
        Property("PermissionsIsotopeAccess", BooleanType),
        Property("PermissionsIsotopeLEX", BooleanType),
        Property("PermissionsQuipMetricsAccess", BooleanType),
        Property("PermissionsQuipUserEngagementMetrics", BooleanType),
        Property("PermissionsRemoteMediaVirtualDesktop", BooleanType),
        Property("PermissionsTransactionSecurityExempt", BooleanType),
        Property("PermissionsManageStores", BooleanType),
        Property("PermissionsManageExternalConnections", BooleanType),
        Property("PermissionsUseReturnOrder", BooleanType),
        Property("PermissionsUseReturnOrderAPIs", BooleanType),
        Property("PermissionsUseSubscriptionEmails", BooleanType),
        Property("PermissionsUseOrderEntry", BooleanType),
        Property("PermissionsUseRepricing", BooleanType),
        Property("PermissionsAIViewInsightObjects", BooleanType),
        Property("PermissionsAICreateInsightObjects", BooleanType),
        Property("PermissionsViewMLModels", BooleanType),
        Property("PermissionsLifecycleManagementAPIUser", BooleanType),
        Property("PermissionsNativeWebviewScrolling", BooleanType),
        Property("PermissionsViewDeveloperName", BooleanType),
        Property("PermissionsBypassMFAForUiLogins", BooleanType),
        Property("PermissionsClientSecretRotation", BooleanType),
        Property("PermissionsAccessToServiceProcess", BooleanType),
        Property("PermissionsManageOrchInstsAndWorkItems", BooleanType),
        Property("PermissionsManageDataspaceScope", BooleanType),
        Property("PermissionsConfigureDataspaceScope", BooleanType),
        Property("PermissionsEditRepricing", BooleanType),
        Property("PermissionsEnableIPFSUpload", BooleanType),
        Property("PermissionsEnableBCTransactionPolling", BooleanType),
        Property("PermissionsFSCArcGraphCommunityUser", BooleanType),
        Property("LastViewedDate", StringType),
        Property("Name", StringType),
        Property("UserLicenseId", StringType),
        Property("UserType", StringType),
        Property("CreatedDate", StringType),
        Property("CreatedById", StringType),
        Property("LastModifiedDate", StringType),
        Property("LastModifiedById", StringType),
        Property("SystemModstamp", StringType),
    ).to_dict()

    @property
    def url_base(self):
        domain = self.config["domain"]
        url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"
        return url

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """
        We can send a POST request with headers, payload, and access token to /jobs/query path to create a job id
        We can send a GET request to jobs/query/jobid/results path to get the bulk data in csv
        We have a while statemnet which does that and gets the job id which has the bulk data
        We can load the csv data into json with parse_response function
        We can load the json data with get_records function
        """

        def get_job_id(self):
            """
            We can get the job id in this function and pass it to the child class to get the bulk data
            """

            job_id_list = []
            domain = self.config["domain"]

            access_token = self.authenticator._auth_headers.get("Authorization").split("Bearer ")[1]

            columns = """
                          Id,Description,LastReferencedDate,PermissionsEmailSingle,PermissionsEmailMass,PermissionsEditTask,PermissionsEditEvent,
                          PermissionsExportReport,PermissionsImportPersonal,PermissionsDataExport,PermissionsManageUsers,PermissionsEditPublicFilters,
                          PermissionsEditPublicTemplates,PermissionsModifyAllData,PermissionsEditBillingInfo,PermissionsManageCases,
                          PermissionsMassInlineEdit,PermissionsEditKnowledge,PermissionsManageKnowledge,PermissionsManageSolutions,
                          PermissionsCustomizeApplication,PermissionsEditReadonlyFields,PermissionsRunReports,PermissionsViewSetup,
                          PermissionsTransferAnyEntity,PermissionsNewReportBuilder,PermissionsActivateContract,PermissionsActivateOrder,
                          PermissionsImportLeads,PermissionsManageLeads,PermissionsTransferAnyLead,PermissionsViewAllData,PermissionsEditPublicDocuments,
                          PermissionsViewEncryptedData,PermissionsEditBrandTemplates,PermissionsEditHtmlTemplates,PermissionsChatterInternalUser,
                          PermissionsManageEncryptionKeys,PermissionsDeleteActivatedContract,PermissionsChatterInviteExternalUsers,
                          PermissionsSendSitRequests,PermissionsApiUserOnly,PermissionsManageRemoteAccess,PermissionsCanUseNewDashboardBuilder,
                          PermissionsManageCategories,PermissionsConvertLeads,PermissionsPasswordNeverExpires,PermissionsUseTeamReassignWizards,
                          PermissionsEditActivatedOrders,PermissionsInstallMultiforce,PermissionsPublishMultiforce,PermissionsChatterOwnGroups,
                          PermissionsEditOppLineItemUnitPrice,PermissionsCreateMultiforce,PermissionsBulkApiHardDelete,PermissionsSolutionImport,
                          PermissionsManageCallCenters,PermissionsManageSynonyms,PermissionsViewContent,PermissionsManageEmailClientConfig,
                          PermissionsEnableNotifications,PermissionsManageDataIntegrations,PermissionsDistributeFromPersWksp,PermissionsViewDataCategories,
                          PermissionsManageDataCategories,PermissionsAuthorApex,PermissionsManageMobile,PermissionsApiEnabled,PermissionsManageCustomReportTypes,
                          PermissionsEditCaseComments,PermissionsTransferAnyCase,PermissionsContentAdministrator,PermissionsCreateWorkspaces,
                          PermissionsManageContentPermissions,PermissionsManageContentProperties,PermissionsManageContentTypes,PermissionsManageExchangeConfig,
                          PermissionsManageAnalyticSnapshots,PermissionsScheduleReports,PermissionsManageBusinessHourHolidays,PermissionsManageEntitlements,
                          PermissionsManageDynamicDashboards,PermissionsCustomSidebarOnAllPages,PermissionsManageInteraction,PermissionsViewMyTeamsDashboards,
                          PermissionsModerateChatter,PermissionsResetPasswords,PermissionsFlowUFLRequired,PermissionsCanInsertFeedSystemFields,
                          PermissionsActivitiesAccess,PermissionsManageKnowledgeImportExport,PermissionsEmailTemplateManagement,PermissionsEmailAdministration,
                          PermissionsManageChatterMessages,PermissionsAllowEmailIC,PermissionsChatterFileLink,PermissionsForceTwoFactor,
                          PermissionsViewEventLogFiles,PermissionsManageNetworks,PermissionsManageAuthProviders,PermissionsRunFlow,
                          PermissionsCreateCustomizeDashboards,PermissionsCreateDashboardFolders,PermissionsViewPublicDashboards,
                          PermissionsManageDashbdsInPubFolders,PermissionsCreateCustomizeReports,PermissionsCreateReportFolders,PermissionsViewPublicReports,
                          PermissionsManageReportsInPubFolders,PermissionsEditMyDashboards,PermissionsEditMyReports,PermissionsViewAllUsers,
                          PermissionsAllowUniversalSearch,PermissionsConnectOrgToEnvironmentHub,PermissionsWorkCalibrationUser,PermissionsCreateCustomizeFilters,
                          PermissionsWorkDotComUserPerm,PermissionsContentHubUser,PermissionsGovernNetworks,PermissionsSalesConsole,
                          PermissionsTwoFactorApi,PermissionsDeleteTopics,PermissionsEditTopics,PermissionsCreateTopics,PermissionsAssignTopics,
                          PermissionsIdentityEnabled,PermissionsIdentityConnect,PermissionsAllowViewKnowledge,PermissionsContentWorkspaces,
                          PermissionsManageSearchPromotionRules,PermissionsCustomMobileAppsAccess,PermissionsViewHelpLink,PermissionsManageProfilesPermissionsets,
                          PermissionsAssignPermissionSets,PermissionsManageRoles,PermissionsManageIpAddresses,PermissionsManageSharing,
                          PermissionsManageInternalUsers,PermissionsManagePasswordPolicies,PermissionsManageLoginAccessPolicies,PermissionsViewPlatformEvents,
                          PermissionsManageCustomPermissions,PermissionsCanVerifyComment,PermissionsManageUnlistedGroups,PermissionsStdAutomaticActivityCapture,
                          PermissionsInsightsAppDashboardEditor,PermissionsManageTwoFactor,PermissionsInsightsAppUser,PermissionsInsightsAppAdmin,
                          PermissionsInsightsAppEltEditor,PermissionsInsightsAppUploadUser,PermissionsInsightsCreateApplication,PermissionsLightningExperienceUser,
                          PermissionsViewDataLeakageEvents,PermissionsConfigCustomRecs,PermissionsSubmitMacrosAllowed,PermissionsBulkMacrosAllowed,
                          PermissionsShareInternalArticles,PermissionsManageSessionPermissionSets,PermissionsManageTemplatedApp,PermissionsUseTemplatedApp,
                          PermissionsSendAnnouncementEmails,PermissionsChatterEditOwnPost,PermissionsChatterEditOwnRecordPost,PermissionsWaveTabularDownload,
                          PermissionsAutomaticActivityCapture,PermissionsImportCustomObjects,PermissionsDelegatedTwoFactor,PermissionsChatterComposeUiCodesnippet,
                          PermissionsSelectFilesFromSalesforce,PermissionsModerateNetworkUsers,PermissionsMergeTopics,PermissionsSubscribeToLightningReports,
                          PermissionsManagePvtRptsAndDashbds,PermissionsAllowLightningLogin,PermissionsCampaignInfluence2,PermissionsViewDataAssessment,
                          PermissionsRemoveDirectMessageMembers,PermissionsCanApproveFeedPost,PermissionsAddDirectMessageMembers,PermissionsAllowViewEditConvertedLeads,
                          PermissionsShowCompanyNameAsUserBadge,PermissionsAccessCMC,PermissionsViewHealthCheck,PermissionsManageHealthCheck,
                          PermissionsPackaging2,PermissionsManageCertificates,PermissionsCreateReportInLightning,PermissionsPreventClassicExperience,
                          PermissionsHideReadByList,PermissionsListEmailSend,PermissionsFeedPinning,PermissionsChangeDashboardColors,
                          PermissionsManageRecommendationStrategies,PermissionsManagePropositions,PermissionsCloseConversations,PermissionsSubscribeReportRolesGrps,
                          PermissionsSubscribeDashboardRolesGrps,PermissionsUseWebLink,PermissionsHasUnlimitedNBAExecutions,PermissionsViewOnlyEmbeddedAppUser,
                          PermissionsViewAllActivities,PermissionsSubscribeReportToOtherUsers,PermissionsLightningConsoleAllowedForUser,
                          PermissionsSubscribeReportsRunAsUser,PermissionsSubscribeToLightningDashboards,PermissionsSubscribeDashboardToOtherUsers,
                          PermissionsCreateLtngTempInPub,PermissionsAppointmentBookingUserAccess,PermissionsTransactionalEmailSend,
                          PermissionsViewPrivateStaticResources,PermissionsCreateLtngTempFolder,PermissionsApexRestServices,PermissionsConfigureLiveMessage,
                          PermissionsLiveMessageAgent,PermissionsEnableCommunityAppLauncher,PermissionsGiveRecognitionBadge,PermissionsLightningSchedulerUserAccess,
                          PermissionsUseMySearch,PermissionsLtngPromoReserved01UserPerm,PermissionsManageSubscriptions,PermissionsWaveManagePrivateAssetsUser,
                          PermissionsCanEditDataPrepRecipe,PermissionsAddAnalyticsRemoteConnections,PermissionsManageSurveys,PermissionsUseAssistantDialog,
                          PermissionsUseQuerySuggestions,PermissionsPackaging2PromoteVersion,PermissionsRecordVisibilityAPI,PermissionsViewRoles,
                          PermissionsCanManageMaps,PermissionsLMOutboundMessagingUserPerm,PermissionsModifyDataClassification,PermissionsPrivacyDataAccess,
                          PermissionsQueryAllFiles,PermissionsModifyMetadata,PermissionsManageCMS,PermissionsSandboxTestingInCommunityApp,
                          PermissionsCanEditPrompts,PermissionsViewUserPII,PermissionsManageHubConnections,PermissionsB2BMarketingAnalyticsUser,
                          PermissionsTraceXdsQueries,PermissionsViewSecurityCommandCenter,PermissionsManageSecurityCommandCenter,PermissionsViewAllCustomSettings,
                          PermissionsViewAllForeignKeyNames,PermissionsAddWaveNotificationRecipients,PermissionsHeadlessCMSAccess,PermissionsLMEndMessagingSessionUserPerm,
                          PermissionsConsentApiUpdate,PermissionsPaymentsAPIUser,PermissionsAccessContentBuilder,PermissionsAccountSwitcherUser,
                          PermissionsViewAnomalyEvents,PermissionsManageC360AConnections,PermissionsIsContactCenterAdmin,PermissionsIsContactCenterAgent,
                          PermissionsManageReleaseUpdates,PermissionsViewAllProfiles,PermissionsSkipIdentityConfirmation,PermissionsCanToggleCallRecordings,
                          PermissionsLearningManager,PermissionsSendCustomNotifications,PermissionsPackaging2Delete,PermissionsUseOmnichannelInventoryAPIs,
                          PermissionsViewRestrictionAndScopingRules,PermissionsFSCComprehensiveUserAccess,PermissionsBotManageBots,
                          PermissionsBotManageBotsTrainingData,PermissionsSchedulingLineAmbassador,PermissionsSchedulingFacilityManager,
                          PermissionsOmnichannelInventorySync,PermissionsManageLearningReporting,PermissionsIsContactCenterSupervisor,
                          PermissionsIsotopeCToCUser,PermissionsCanAccessCE,PermissionsUseAddOrderItemSummaryAPIs,PermissionsIsotopeAccess,
                          PermissionsIsotopeLEX,PermissionsQuipMetricsAccess,PermissionsQuipUserEngagementMetrics,PermissionsRemoteMediaVirtualDesktop,
                          PermissionsTransactionSecurityExempt,PermissionsManageStores,PermissionsManageExternalConnections,PermissionsUseReturnOrder,
                          PermissionsUseReturnOrderAPIs,PermissionsUseSubscriptionEmails,PermissionsUseOrderEntry,PermissionsUseRepricing,
                          PermissionsAIViewInsightObjects,PermissionsAICreateInsightObjects,PermissionsViewMLModels,PermissionsLifecycleManagementAPIUser,
                          PermissionsNativeWebviewScrolling,PermissionsViewDeveloperName,PermissionsBypassMFAForUiLogins,PermissionsClientSecretRotation,
                          PermissionsAccessToServiceProcess,PermissionsManageOrchInstsAndWorkItems,PermissionsManageDataspaceScope,PermissionsConfigureDataspaceScope,
                          PermissionsEditRepricing,PermissionsEnableIPFSUpload,PermissionsEnableBCTransactionPolling,PermissionsFSCArcGraphCommunityUser,
                          LastViewedDate,Name,UserLicenseId,UserType,CreatedDate,CreatedById,LastModifiedDate,LastModifiedById,SystemModstamp

                      """
            entity = "PROFILE"

            headers = get_headers(access_token)
            payload = json.dumps(
                {"operation": "query", "query": f"SELECT {columns} FROM {entity}"}
            )
            url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query"

            response = requests.request("POST", url, headers=headers, data=payload)
            job_id = response.json()["id"]
            self.logger.info(
                f"Job ID fetched for {entity}. Sending the call for result"
            )

            while not job_id_list:
                """
                We can check if a job id has bulk data and return that job id if it has it
                """

                time.sleep(10)
                job_id_url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                job_id_response = requests.request("GET", job_id_url, headers=headers)

                if job_id_response.status_code == 200:
                    job_id_list.append(job_id)
                    self.logger.info("Bulk API - Created Data Job")

            return job_id_list[0]

        job_id = get_job_id(self)

        class BulkResults(SalesforceStream):
            name = "profiles_bulk"
            path = ""

            @property
            def url_base(self):
                domain = self.config["domain"]
                url = f"https://{domain}.salesforce.com/services/data/v58.0/jobs/query/{job_id}/results"
                return url

            def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
                """
                We can load the csv response into json and return it for get_records function
                """

                if len(response.text) > 0:
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    data_list = [row for row in reader]
                    self.logger.info("Bulk API - Updated CSV response to JSON")
                    return data_list
                else:
                    self.logger.info("Bulk API - Empty response")
                    return []

        bulk_results_stream = BulkResults(self._tap, schema={"properties": {}})

        try:
            for record in bulk_results_stream.get_records(context):
                yield record
        except Exception as e:
            pass
            self.logger.info(e)
