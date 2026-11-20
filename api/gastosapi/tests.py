from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.test import TestCase
from unittest.mock import patch

from .models import Account, AccountMovement, AuthToken, Category, CategoryType, Team, TeamMember


class CategoryApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="secret")
        self.team = Team.objects.create(name="Equipo", access_key="clave")
        TeamMember.objects.create(
            team=self.team,
            member=self.user,
            is_team_owner=True,
            created_by=self.user,
        )
        self.token = AuthToken.objects.create(user=self.user)
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {self.token.key}"}

    def payload(self, **overrides):
        data = {
            "team_id": self.team.pk,
            "name": "Comida",
            "type": CategoryType.EXPENSE,
            "icon": "food",
            "color": "#FF0000",
        }
        data.update(overrides)
        return data

    def test_bulk_create_categories(self):
        response = self.client.post(
            "/api/categories/bulk",
            [self.payload(name="Comida"), self.payload(name="Transporte")],
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(Category.objects.filter(team=self.team).count(), 2)
        self.assertTrue(all(c.created_by == self.user for c in Category.objects.all()))

    def test_bulk_create_rejects_invalid_type(self):
        response = self.client.post(
            "/api/categories/bulk",
            [self.payload(type="INVALID")],
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Category.objects.count(), 0)

    def test_bulk_create_rejects_empty_list(self):
        response = self.client.post(
            "/api/categories/bulk",
            [],
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 400)

    def test_list_filters_by_name_and_type(self):
        category = Category.objects.create(**self.payload(), created_by=self.user)
        Category.objects.create(**self.payload(name="Sueldo", type=CategoryType.INCOME), created_by=self.user)

        response = self.client.get(
            "/api/categories/",
            {"name": "comid", "type": CategoryType.EXPENSE},
            **self.auth,
        )

        self.assertEqual(response.status_code, 200)
        results = response.json()["items"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], category.pk)

    def test_list_rejects_invalid_type_filter(self):
        response = self.client.get(
            "/api/categories/",
            {"type": "INVALID"},
            **self.auth,
        )
        self.assertEqual(response.status_code, 400)


class AccountApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="account-tester", password="secret")
        self.team = Team.objects.create(name="Equipo cuenta", access_key="clave")
        TeamMember.objects.create(
            team=self.team,
            member=self.user,
            is_team_owner=True,
            created_by=self.user,
        )
        self.token = AuthToken.objects.create(user=self.user)
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {self.token.key}"}

    def payload(self, **overrides):
        data = {
            "team_id": self.team.pk,
            "name": "Cuenta principal",
            "currency": "NIO",
            "opening_price": "100.00",
            "icon": "bank",
            "color": "#00FF00",
        }
        data.update(overrides)
        return data

    def test_create_account_creates_opening_movement(self):
        response = self.client.post(
            "/api/accounts/",
            self.payload(),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 201)
        account = Account.objects.get(pk=response.json()["id"])
        movement = AccountMovement.objects.get(account=account)
        self.assertEqual(str(movement.amount), "100.00")
        self.assertEqual(movement.reference, "Opening Balance")

    def test_create_account_without_opening_balance_has_no_movement(self):
        response = self.client.post(
            "/api/accounts/",
            self.payload(opening_price="0.00"),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 201)
        account = Account.objects.get(pk=response.json()["id"])
        self.assertFalse(AccountMovement.objects.filter(account=account).exists())

    @patch(
        "gastosapi.routers.accounts.AccountMovement.objects.create",
        side_effect=DatabaseError("movement insert failed"),
    )
    def test_create_account_rolls_back_when_opening_movement_fails(self, _create_movement):
        response = self.client.post(
            "/api/accounts/",
            self.payload(),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 500)
        self.assertFalse(Account.objects.filter(team=self.team, name="Cuenta principal").exists())
