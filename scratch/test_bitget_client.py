import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Setup path to backend
sys.path.append(r"c:\Users\USER\OneDrive\Desktop\councilB\backend")

from app.api.services.bitget_service import BitgetService

class TestBitgetService(unittest.TestCase):
    
    @patch.dict(os.environ, {
        "BITGET_API_KEY": "test-key",
        "BITGET_API_SECRET": "test-secret",
        "BITGET_PASSPHRASE": "test-passphrase",
        "BITGET_IS_SANDBOX": "True"
    })
    def test_signature_generation(self):
        print("--- Test: Bitget HMAC-SHA256 Signature Math ---")
        service = BitgetService()
        self.assertTrue(service.is_configured)
        self.assertTrue(service.is_sandbox)
        
        # Test signature algorithm
        timestamp = "1672531199000"
        method = "POST"
        request_path = "/api/v2/spot/trade/place-order"
        body = '{"symbol":"BTCUSDT","side":"buy"}'
        
        sig = service._generate_signature(timestamp, method, request_path, body)
        self.assertIsNotNone(sig)
        self.assertTrue(len(sig) > 10)
        print(f"[OK] Generated valid base64 signature string: {sig}")

    @patch.dict(os.environ, {}, clear=True)
    def test_dry_run_mode(self):
        print("\n--- Test: Bitget Dry Run Mock Mode ---")
        # Ensure env is empty of Bitget keys
        service = BitgetService()
        self.assertFalse(service.is_configured)
        
        # Place order in dry-run
        res = service.place_spot_order("BTC", "buy", 0.5, 42000.0)
        self.assertTrue(res["success"])
        self.assertTrue(res["order_id"].startswith("mock-bitget-"))
        self.assertEqual(res["symbol"], "BTCUSDT")
        self.assertEqual(res["side"], "buy")
        # Size for market BUY should be quote USDT amount = 0.5 * 42000 = 21000.0
        self.assertEqual(float(res["size"]), 21000.0)
        print("[OK] Dry run mode placed order and calculated USDT size correctly.")

    @patch.dict(os.environ, {
        "BITGET_API_KEY": "test-key",
        "BITGET_API_SECRET": "test-secret",
        "BITGET_PASSPHRASE": "test-passphrase",
        "BITGET_IS_SANDBOX": "True"
    })
    @patch("httpx.Client.post")
    def test_mock_api_success(self, mock_post):
        print("\n--- Test: Mock API Order Success ---")
        # Setup mock http response matching Bitget code 00000 success response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "code": "00000",
            "msg": "success",
            "data": {
                "orderId": "1234567890",
                "clientOid": "cl12345"
            }
        }
        mock_post.return_value = mock_resp
        
        service = BitgetService()
        res = service.place_spot_order("ETH", "sell", 1.5, 3000.0)
        
        self.assertTrue(res["success"])
        self.assertEqual(res["order_id"], "1234567890")
        self.assertEqual(res["symbol"], "ETHUSDT")
        self.assertEqual(res["side"], "sell")
        # Size for market SELL should be base quantity = 1.5
        self.assertEqual(float(res["size"]), 1.5)
        print("[OK] Mock API order success processed correctly.")

def run_tests():
    print("=== STARTING BITGET SERVICE TESTS ===")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBitgetService)
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
    print("=== ALL BITGET SERVICE TESTS PASSED ===")

if __name__ == "__main__":
    run_tests()
