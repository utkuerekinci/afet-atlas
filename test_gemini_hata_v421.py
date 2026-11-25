import unittest
from atlas_gemini_yorum import hata_mesaji, _gecerli_anahtar, DEFAULT_MODEL

class GeminiErrorChecks(unittest.TestCase):
    def test_model(self):
        self.assertEqual(DEFAULT_MODEL, 'gemini-3.1-flash-lite')
    def test_example_placeholder_rejected(self):
        self.assertEqual(_gecerli_anahtar('AI_STUDIO_API_KEY_BURAYA'), '')
    def test_error_messages(self):
        for code, fragment in [(401,'geçersiz'), (403,'reddetti'), (404,'model'), (429,'kota'), (503,'servisi')]:
            info, detail = hata_mesaji(RuntimeError(f'{code} ERROR'))
            self.assertIn(fragment, info.lower())
    def test_mask_real_secret(self):
        key = 'AIzaABCDEF1234567890123456789012345678'
        info, detail = hata_mesaji(RuntimeError(f'500 error from api_key={key}'), key)
        self.assertNotIn(key, detail)
    def test_module_import_error(self):
        info, _ = hata_mesaji(ModuleNotFoundError('No module named google.genai'))
        self.assertIn('pip install', info)

if __name__ == '__main__': unittest.main()
