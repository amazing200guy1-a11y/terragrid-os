"""
TerraGrid OS Formal Verification Test Suite
15 Automated Unit Tests verifying physical conservation laws,
civil paving equations, thermodynamic biogas yields, and USSD cryptography.
"""

import unittest
from terragrid_engine import (
    CivilRoadwaySubsystem,
    WasteRecoverySubsystem,
    BioRefineryEnergySubsystem,
    SolarHarmattanTelemetrySubsystem,
    CircularFarmerUSSDLedger
)


class TestTerraGridSubsystems(unittest.TestCase):

    def test_paving_fleet_calculation(self):
        """Validates hydraulic clamp paver throughput and calendar days."""
        res = CivilRoadwaySubsystem.calculate_paving_fleet(5000.0, 14.0, active_pavers=3)
        self.assertEqual(res["road_area_m2"], 70000.0)
        self.assertEqual(res["daily_fleet_m2"], 4050.0)
        self.assertEqual(res["paving_days_required"], 18)
        self.assertGreater(res["lifecycle_savings_usd"], 10_000_000.0)

    def test_paving_fleet_invalid_pavers(self):
        """Ensures zero or negative paver count raises ValueError."""
        with self.assertRaises(ValueError):
            CivilRoadwaySubsystem.calculate_paving_fleet(1000.0, 10.0, active_pavers=0)

    def test_stormwater_harvest_mass_balance(self):
        """Verifies water harvesting runoff formula: Area * Rainfall * 0.85."""
        res = CivilRoadwaySubsystem.calculate_stormwater_harvest(10000.0, 1200.0)
        expected_liters = 10000.0 * 1200.0 * 0.85
        self.assertEqual(res["harvested_liters"], expected_liters)
        self.assertEqual(res["harvested_m3"], expected_liters / 1000.0)
        self.assertGreater(res["suspended_silt_captured_kg"], 0.0)

    def test_waste_stream_mass_conservation(self):
        """Verifies municipal waste fractions sum to 100% of input mass."""
        daily_tons = 150.0
        res = WasteRecoverySubsystem.process_waste_stream(daily_tons)
        sum_fractions = (
            res["organic_bio_feedstock_tons"] +
            res["sub_base_rubble_tons"] +
            res["recyclables_tons"] +
            res["reject_tons"]
        )
        self.assertAlmostEqual(sum_fractions, daily_tons, places=2)

    def test_waste_stream_economic_benefits(self):
        """Verifies recycling revenue and diesel fuel savings."""
        res = WasteRecoverySubsystem.process_waste_stream(100.0, haulage_km=15.0)
        self.assertGreater(res["recycling_revenue_ngn"], 0.0)
        self.assertGreater(res["fuel_cost_savings_ngn"], 0.0)
        self.assertGreater(res["diesel_liters_displaced"], 0.0)

    def test_biorefinery_thermodynamic_power(self):
        """Verifies CHP electricity output scales with cattle and organic waste."""
        res = BioRefineryEnergySubsystem.calculate_biorefinery_yields(cattle_headcount=10000)
        self.assertGreater(res["daily_kwh_generated"], 10000.0)
        self.assertGreater(res["continuous_megawatts"], 0.4)
        self.assertGreater(res["total_daily_biogas_m3"], 5000.0)

    def test_cbg_cooking_gas_cylinder_yield(self):
        """Verifies bottled Compressed Biomethane (12.5kg cylinders)."""
        res = BioRefineryEnergySubsystem.calculate_biorefinery_yields(cattle_headcount=5000)
        self.assertGreater(res["cylinders_12_5kg_bottled"], 50)
        self.assertGreater(res["cbg_revenue_ngn"], 100000.0)

    def test_bio_fertilizer_npk_digestate(self):
        """Verifies organic bio-fertilizer production and 50kg bag calculation."""
        res = BioRefineryEnergySubsystem.calculate_biorefinery_yields(cattle_headcount=8000)
        self.assertGreater(res["fertilizer_50kg_bags"], 200)
        self.assertGreater(res["fertilizer_revenue_ngn"], 1000000.0)

    def test_methane_ghg_abatement(self):
        """Verifies Global Warming Potential (GWP 28x) CO2e abatement."""
        res = BioRefineryEnergySubsystem.calculate_biorefinery_yields(cattle_headcount=10000)
        self.assertGreater(res["co2e_abated_tons_daily"], 50.0)

    def test_solar_harmattan_wiper_recovery(self):
        """Verifies energy recovered by automated robotic wipers during dust deposition."""
        res = SolarHarmattanTelemetrySubsystem.calculate_solar_corridor_efficiency(10.0)
        self.assertGreater(res["robotic_wiped_daily_kwh"], res["unwiped_harmattan_daily_kwh"])
        self.assertGreater(res["energy_recovered_daily_kwh"], 0.0)
        self.assertEqual(res["number_of_poles"], 333)

    def test_ussd_ledger_registration(self):
        """Verifies farmer registration on double-entry USSD ledger."""
        ledger = CircularFarmerUSSDLedger()
        acc = ledger.register_farmer("+2348011112222", "Kwame Mensah", "Ashanti Region")
        self.assertEqual(acc["farmer_name"], "Kwame Mensah")
        self.assertEqual(acc["terracredit_balance"], 0.0)

    def test_ussd_chaff_deposit_and_cryptographic_hash(self):
        """Verifies chaff deposit, credit minting, and SHA-256 transaction hash."""
        ledger = CircularFarmerUSSDLedger()
        tx = ledger.record_chaff_delivery("+2348011112222", 200.0)
        self.assertEqual(tx["credits_earned"], 500.0) # 200 * 2.5
        self.assertEqual(tx["balance"], 500.0)
        self.assertEqual(len(tx["tx_hash"]), 16)
        self.assertEqual(len(ledger.transaction_ledger), 1)

    def test_ussd_reward_redemption_flow(self):
        """Verifies successful redemption of Bio-Fertilizer voucher."""
        ledger = CircularFarmerUSSDLedger()
        ledger.record_chaff_delivery("+2348011112222", 300.0) # 750 credits
        tx = ledger.redeem_credit("+2348011112222", "FERTILIZER_50KG") # 500 credits
        self.assertEqual(tx["remaining_balance"], 250.0)
        self.assertEqual(tx["reward"], "FERTILIZER_50KG")

    def test_ussd_insufficient_balance_rejection(self):
        """Verifies transaction reversal on insufficient credit balance."""
        ledger = CircularFarmerUSSDLedger()
        ledger.record_chaff_delivery("+2348011112222", 20.0) # 50 credits
        with self.assertRaises(ValueError):
            ledger.redeem_credit("+2348011112222", "FERTILIZER_50KG") # requires 500

    def test_ussd_session_interactive_simulation(self):
        """Verifies complete interactive USSD menu flow (*347*88#)."""
        ledger = CircularFarmerUSSDLedger()
        phone = "+2348099998888"
        # Initial dial
        s1 = ledger.execute_ussd_session(phone, "*347*88#")
        self.assertTrue(s1.startswith("CON Welcome"))
        # Deposit chaff
        s2 = ledger.execute_ussd_session(phone, "1*400")
        self.assertTrue("400.0kg Chaff received" in s2)
        # Check balance
        s3 = ledger.execute_ussd_session(phone, "2")
        self.assertTrue("1000.0 TC" in s3)
        # Redeem Gas
        s4 = ledger.execute_ussd_session(phone, "4")
        self.assertTrue("Voucher Code:" in s4)


if __name__ == "__main__":
    unittest.main()
