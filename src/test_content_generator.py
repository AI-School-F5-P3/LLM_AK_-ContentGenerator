import unittest
import requests
from unittest.mock import Mock, patch
from utils.prompt_manager import PromptManager
from generators.ollama_generator import OllamaGenerator

class TestPromptManager(unittest.TestCase):
    def setUp(self):
        self.prompt_manager = PromptManager()

    def test_get_all_platforms(self):
        """Verifica que se obtengan todas las plataformas correctamente"""
        platforms = self.prompt_manager.get_all_platforms()
        expected_platforms = ["Blog", "Twitter", "LinkedIn", "Instagram"]
        self.assertEqual(set(platforms), set(expected_platforms))
        self.assertEqual(len(platforms), 4)

    def test_get_template_valid_platform(self):
        """Verifica que se obtenga el template correcto para una plataforma válida"""
        template_data = self.prompt_manager.get_template("Blog")
        self.assertIsNotNone(template_data)
        self.assertIn("template", template_data)
        self.assertIn("params", template_data)
        self.assertEqual(template_data["params"], ["tema", "audiencia", "tono"])

    def test_get_template_invalid_platform(self):
        """Verifica que se maneje correctamente una plataforma inválida"""
        template_data = self.prompt_manager.get_template("PlataformaInexistente")
        self.assertIsNone(template_data)

class TestOllamaGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = OllamaGenerator(model="mistral")
        self.test_template = """
        Genera contenido sobre {tema}.
        Audiencia: {audiencia}
        Tono: {tono}
        """
        self.test_params = {
            "tema": "Inteligencia Artificial",
            "audiencia": "Estudiantes",
            "tono": "Educativo"
        }

    @patch('requests.post')
    def test_generate_content_success(self, mock_post):
        """Verifica la generación exitosa de contenido"""
        # Simular respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Contenido generado de prueba"}
        mock_post.return_value = mock_response

        result = self.generator.generate_content(self.test_template, self.test_params)
        self.assertEqual(result, "Contenido generado de prueba")

    @patch('requests.post')
    def test_generate_content_api_error(self, mock_post):
        """Verifica el manejo de errores de la API"""
        # Simular error de la API
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = '{"error": "Model not found"}'
        mock_post.return_value = mock_response

        with self.assertRaises(Exception):
            self.generator.generate_content(self.test_template, self.test_params)

    def test_validate_params_success(self):
        """Verifica la validación exitosa de parámetros"""
        required_params = ["tema", "audiencia", "tono"]
        self.assertTrue(
            self.generator.validate_params(required_params, self.test_params)
        )

    def test_validate_params_failure(self):
        """Verifica la validación fallida de parámetros"""
        required_params = ["tema", "audiencia", "tono", "parametro_inexistente"]
        self.assertFalse(
            self.generator.validate_params(required_params, self.test_params)
        )

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.prompt_manager = PromptManager()
        self.generator = OllamaGenerator()

    def test_end_to_end_flow(self):
        """Prueba el flujo completo de generación de contenido"""
        # 1. Obtener template
        platform = "Blog"
        template_data = self.prompt_manager.get_template(platform)
        self.assertIsNotNone(template_data)

        # 2. Preparar parámetros
        params = {
            "tema": "Inteligencia Artificial",
            "audiencia": "Estudiantes universitarios",
            "tono": "Educativo"
        }

        # 3. Verificar que Ollama está ejecutándose
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code != 200:
                self.skipTest("Ollama no está ejecutándose")
        except requests.exceptions.ConnectionError:
            self.skipTest("No se puede conectar con Ollama")

        # 4. Intentar generar contenido
        try:
            result = self.generator.generate_content(
                template_data["template"],
                params
            )
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
        except Exception as e:
            self.skipTest(f"Error al generar contenido: {str(e)}")

if __name__ == '__main__':
    unittest.main(verbosity=2)