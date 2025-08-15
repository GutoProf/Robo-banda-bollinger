import unittest
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from src.ai_model import extrair_caracteristicas, treinar_modelo, carregar_modelo, prever_qualidade_sinal

class TestAIModel(unittest.TestCase):
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Criar dados de exemplo para treinamento
        self.dados_trades_exemplo = pd.DataFrame({
            'bb_position': np.random.rand(50),
            'adx': np.random.rand(50) * 50,
            'volatility': np.random.rand(50) * 0.1,
            'day_of_week': np.random.randint(0, 7, 50),
            'hour': np.random.randint(0, 24, 50),
            'resultado': np.random.randint(0, 2, 50)  # 0 ou 1
        })
        
        # Criar DataFrame com dados para previsão
        self.caracteristicas_exemplo = {
            'bb_position': 0.3,
            'adx': 25.0,
            'volatility': 0.05,
            'day_of_week': 2,  # Quarta-feira
            'hour': 10
        }

    def test_extrair_caracteristicas(self):
        """
        Testa se a função extrair_caracteristicas extrai as características corretamente.
        """
        # Criar DataFrame de exemplo com dados de preços e indicadores
        df_exemplo = pd.DataFrame({
            'time': pd.date_range(start='2023-01-01', periods=100, freq='D'),
            'open': np.random.rand(100) * 100,
            'high': np.random.rand(100) * 100 + 10,
            'low': np.random.rand(100) * 100 - 10,
            'close': np.random.rand(100) * 100,
            'bb_upper': np.random.rand(100) * 100 + 5,
            'bb_middle': np.random.rand(100) * 100,
            'bb_lower': np.random.rand(100) * 100 - 5,
            'adx': np.random.rand(100) * 50
        })
        
        # Testar extração de características
        caracteristicas = extrair_caracteristicas(df_exemplo, 50)
        
        # Verificar se as características foram extraídas
        self.assertIsNotNone(caracteristicas)
        self.assertIn('bb_position', caracteristicas)
        self.assertIn('adx', caracteristicas)
        self.assertIn('volatility', caracteristicas)
        self.assertIn('day_of_week', caracteristicas)
        self.assertIn('hour', caracteristicas)

    def test_treinar_modelo(self):
        """
        Testa se a função treinar_modelo treina um modelo corretamente.
        """
        # Treinar o modelo
        modelo = treinar_modelo(self.dados_trades_exemplo)
        
        # Verificar se o modelo foi criado
        self.assertIsNotNone(modelo)
        self.assertIsInstance(modelo, RandomForestClassifier)
        
        # Verificar se o modelo foi salvo
        self.assertTrue(os.path.exists("models/bollinger_ai.pkl"))

    def test_carregar_modelo(self):
        """
        Testa se a função carregar_modelo carrega um modelo salvo.
        """
        # Primeiro, garantir que há um modelo salvo
        if not os.path.exists("models/bollinger_ai.pkl"):
            treinar_modelo(self.dados_trades_exemplo)
        
        # Carregar o modelo
        modelo = carregar_modelo()
        
        # Verificar se o modelo foi carregado
        self.assertIsNotNone(modelo)
        self.assertIsInstance(modelo, RandomForestClassifier)

    def test_prever_qualidade_sinal(self):
        """
        Testa se a função prever_qualidade_sinal faz previsões corretamente.
        """
        # Treinar um modelo para teste
        modelo = treinar_modelo(self.dados_trades_exemplo)
        
        # Fazer uma previsão
        previsao = prever_qualidade_sinal(modelo, self.caracteristicas_exemplo)
        
        # Verificar se a previsão é válida (0 ou 1)
        self.assertIn(previsao, [0, 1])

if __name__ == '__main__':
    # Criar diretórios necessários para os testes
    os.makedirs("models", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    unittest.main()