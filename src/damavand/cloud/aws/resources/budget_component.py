from typing import Optional
from functools import cached_property
from dataclasses import dataclass
from enum import StrEnum

import pulumi_aws as aws
from pulumi import ComponentResource as PulumiComponentResource
from pulumi import ResourceOptions


class BudgetTimeUnit(StrEnum):
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "ANNUALLY"


class BudgetType(StrEnum):
    COST = "COST"
    USAGE = "USAGE"


class BudgetComparisonOperator(StrEnum):
    EQUAL_TO = "EQUAL_TO"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"


class BudgetThresholdType(StrEnum):
    ABSOLUTE_VALUE = "ABSOLUTE_VALUE"
    PERCENTAGE = "PERCENTAGE"


class BudgetNotificationType(StrEnum):
    ACTUAL = "ACTUAL"
    FORECASTED = "FORECASTED"


@dataclass
class AwsBudgetComponentArgs:
    montly_limit_in_dollors: int
    subscriber_emails: list[str]
    filter_tag_key: str
    filter_tag_value: str


class AwsBudgetComponent(PulumiComponentResource):
    def __init__(
        self,
        name: str,
        tags: dict[str, str],
        args: AwsBudgetComponentArgs,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            f"Damavand:{AwsBudgetComponent.__name__}",
            name=name,
            props={},
            opts=opts,
            remote=False,
        )

        self.args = args
        self._tags = tags

        _ = self.daily_budgets
        _ = self.monthly_budgets
        _ = self.quarterly_budgets
        _ = self.yearly_budgets

    @property
    def tags(self) -> dict[str, str]:
        """Return the tags for the component."""

        return self._tags

    @property
    def daily_budget_limit(self) -> int:
        """Return the daily budget limit in dollars. Consider 30 days in a month."""

        return self.args.montly_limit_in_dollors // 30

    @property
    def monthly_budget_limit(self) -> int:
        """Return the monthly budget limit in dollars."""

        return self.args.montly_limit_in_dollors

    @property
    def quarterly_budget_limit(self) -> int:
        """Return the quarterly budget limit in dollars."""

        return self.args.montly_limit_in_dollors * 3

    @property
    def yearly_budget_limit(self) -> int:
        """Return the yearly budget limit in dollars."""

        return self.args.montly_limit_in_dollors * 12

    @cached_property
    def daily_budgets(self) -> list[aws.budgets.Budget]:
        """Return the daily budgets for the component."""

        return [
            aws.budgets.Budget(
                f"{self._name}-daily-budget-%{threshold}",
                opts=ResourceOptions(parent=self),
                name=f"{self._name}-daily-budget-%{threshold}",
                limit_amount=str(self.daily_budget_limit),
                limit_unit="USD",
                time_unit=BudgetTimeUnit.DAILY,
                budget_type=BudgetType.COST,
                notifications=[
                    {
                        "comparison_operator": BudgetComparisonOperator.EQUAL_TO,
                        "threshold": threshold,
                        "threshold_type": BudgetThresholdType.PERCENTAGE,
                        "notification_type": BudgetNotificationType.ACTUAL,
                        "subscriber_email_addresses": self.args.subscriber_emails,
                    }
                ],
                cost_filters=[
                    {
                        "name": "TagKeyValue",
                        "values": [
                            f"{self.args.filter_tag_key}${self.args.filter_tag_value}"
                        ],
                    }
                ],
                tags=self.tags,
            )
            for threshold in [80, 100]
        ]

    @cached_property
    def monthly_budgets(self) -> list[aws.budgets.Budget]:
        """Return the monthly budgets for the component."""

        return [
            aws.budgets.Budget(
                f"{self._name}-monthly-budget-%{threshold}",
                opts=ResourceOptions(parent=self),
                name=f"{self._name}-monthly-budget-%{threshold}",
                limit_amount=str(self.monthly_budget_limit),
                limit_unit="USD",
                time_unit=BudgetTimeUnit.MONTHLY,
                budget_type=BudgetType.COST,
                notifications=[
                    {
                        "comparison_operator": BudgetComparisonOperator.EQUAL_TO,
                        "threshold": threshold,
                        "threshold_type": BudgetThresholdType.PERCENTAGE,
                        "notification_type": BudgetNotificationType.ACTUAL,
                        "subscriber_email_addresses": self.args.subscriber_emails,
                    }
                ],
                cost_filters=[
                    {
                        "name": "TagKeyValue",
                        "values": [
                            f"{self.args.filter_tag_key}${self.args.filter_tag_value}"
                        ],
                    }
                ],
                tags=self.tags,
            )
            for threshold in [90, 95, 99, 100]
        ]

    @cached_property
    def quarterly_budgets(self) -> list[aws.budgets.Budget]:
        """Return the quarterly budgets for the component."""

        return [
            aws.budgets.Budget(
                f"{self._name}-quarterly-budget-%{threshold}",
                opts=ResourceOptions(parent=self),
                name=f"{self._name}-quarterly-budget-%{threshold}",
                limit_amount=str(self.quarterly_budget_limit),
                limit_unit="USD",
                time_unit=BudgetTimeUnit.QUARTERLY,
                budget_type=BudgetType.COST,
                notifications=[
                    {
                        "comparison_operator": BudgetComparisonOperator.EQUAL_TO,
                        "threshold": threshold,
                        "threshold_type": BudgetThresholdType.PERCENTAGE,
                        "notification_type": BudgetNotificationType.ACTUAL,
                        "subscriber_email_addresses": self.args.subscriber_emails,
                    }
                ],
                cost_filters=[
                    {
                        "name": "TagKeyValue",
                        "values": [
                            f"{self.args.filter_tag_key}${self.args.filter_tag_value}"
                        ],
                    }
                ],
                tags=self.tags,
            )
            for threshold in [90, 100]
        ]

    @cached_property
    def yearly_budgets(self) -> list[aws.budgets.Budget]:
        """Return the yearly budgets for the component."""

        return [
            aws.budgets.Budget(
                f"{self._name}-yearly-budget-%{threshold}",
                opts=ResourceOptions(parent=self),
                name=f"{self._name}-yearly-budget-%{threshold}",
                limit_amount=str(self.yearly_budget_limit),
                limit_unit="USD",
                time_unit=BudgetTimeUnit.YEARLY,
                budget_type=BudgetType.COST,
                notifications=[
                    {
                        "comparison_operator": BudgetComparisonOperator.EQUAL_TO,
                        "threshold": threshold,
                        "threshold_type": BudgetThresholdType.PERCENTAGE,
                        "notification_type": BudgetNotificationType.ACTUAL,
                        "subscriber_email_addresses": self.args.subscriber_emails,
                    }
                ],
                cost_filters=[
                    {
                        "name": "TagKeyValue",
                        "values": [
                            f"{self.args.filter_tag_key}${self.args.filter_tag_value}"
                        ],
                    }
                ],
                tags=self.tags,
            )
            for threshold in [90, 100]
        ]
