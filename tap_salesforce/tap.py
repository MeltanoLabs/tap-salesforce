"""Salesforce tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_salesforce import streams

"""
    https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_what_is_rest_api.htm
"""


class TapSalesforce(Tap):
    """Singer Tap for the Salesforce."""

    name = "tap-salesforce"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description=(
                "Client id, used for getting access token if access token is not "
                "available"
            ),
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description=(
                "Client secret, used for getting access token if access token is not "
                "available"
            ),
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest record date to sync",
        ),
        th.Property(
            "end_date",
            th.DateTimeType,
            description="Latest record date to sync",
        ),
        th.Property(
            "domain",
            th.StringType,
            description="Website domain for site url, ie., https://{domain}.salesforce.com/services/data/",
            required=True,
        ),
        th.Property(
            "bulk_load",
            th.BooleanType,
            description="Toggle for using BULK API method",
            required=True,
            default=False,
        ),
        th.Property(
            "auth",
            th.DiscriminatedUnion(
                "flow",
                oauth=th.ObjectType(
                    th.Property(
                        "access_token",
                        th.StringType,
                        required=True,
                        secret=True,
                    ),
                    additional_properties=False,
                ),
                password=th.ObjectType(
                    th.Property("username", th.StringType, required=True),
                    th.Property("password", th.StringType, required=True, secret=True),
                    additional_properties=False,
                ),
            ),
            description=(
                "Auth type for Salesforce API requires either access_token or "
                "username/password"
            ),
            required=True,
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.SalesforceStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        bulk_load = self.config["bulk_load"]
        if bulk_load is True:
            return [
                streams.BulkOpportunityHistoryStream(self),
                streams.BulkAccountStream(self),
                streams.BulkContactStream(self),
                streams.BulkCampaignStream(self),
                streams.BulkEntitlementStream(self),
                streams.BulkCaseStream(self),
                streams.BulkEmailTemplateStream(self),
                streams.BulkFolderStream(self),
                streams.BulkGroupStream(self),
                streams.BulkLeadStream(self),
                streams.BulkPeriodStream(self),
                streams.BulkSolutionStream(self),
                streams.BulkStaticResourceStream(self),
                streams.BulkWebLinkStream(self),
                streams.BulkPricebook2Stream(self),
                streams.BulkProduct2Stream(self),
                streams.BulkPricebookEntryStream(self),
                streams.BulkUserAppInfoStream(self),
                streams.BulkUserRoleStream(self),
                streams.BulkApexClassStream(self),
                streams.BulkApexPageStream(self),
                streams.BulkApexTriggerStream(self),
                streams.BulkCampaignMemberStatusStream(self),
                streams.BulkFiscalYearSettings(self),
                streams.BulkOpportunityStream(self),
                streams.BulkOrganizationStream(self),
                streams.BulkServiceSetupProvisioningStream(self),
                streams.BulkBusinessHoursStream(self),
                streams.BulkUserStream(self),
                streams.BulkProfileStream(self),
            ]
        else:
            return [
                streams.AccountStream(self),
                streams.ContactStream(self),
                streams.CampaignStream(self),
                streams.EntitlementStream(self),
                streams.CaseStream(self),
                streams.EmailTemplateStream(self),
                streams.FolderStream(self),
                streams.GroupStream(self),
                streams.LeadStream(self),
                streams.PeriodStream(self),
                streams.SolutionStream(self),
                streams.StaticResourceStream(self),
                streams.WebLinkStream(self),
                streams.Pricebook2Stream(self),
                streams.Product2Stream(self),
                streams.PricebookEntryStream(self),
                streams.UserAppInfoStream(self),
                streams.UserRoleStream(self),
                streams.ApexClassStream(self),
                streams.ApexPageStream(self),
                streams.ApexTriggerStream(self),
                streams.CampaignMemberStatusStream(self),
                streams.FiscalYearSettingsStream(self),
                streams.OpportunityStream(self),
                streams.OrganizationStream(self),
                streams.ServiceSetupProvisioningStream(self),
                streams.BusinessHoursStream(self),
                streams.UserStream(self),
                streams.ProfileStream(self),
                streams.OpportunityHistoryStream(self),
            ]


if __name__ == "__main__":
    TapSalesforce.cli()
