import unittest
import pandas as pd
import numpy as np
from src.strategy import preparar_dados_para_estrategia, verificar_sinal_compra, verificar_sinal_venda, filtrar_mercado_lateralizado

class TestStrategy(unittest.TestCase):
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Criar um DataFrame de exemplo com dados de preços
        self.df_exemplo = pd.DataFrame({
            'time': pd.date_range(start='2023-01-01', periods=100, freq='D'),
            'open': np.random.rand(100) * 100,
            'high': np.random.rand(100) * 100 + 10,
            'low': np.random.rand(100) * 100 - 10,
            'close': np.random.rand(100) * 100,
            'tick_volume': np.random.randint(1000, 10000, 100)
        })
        
        # Preparar dados com indicadores
        self.df_com_indicadores = preparar_dados_para_estrategia(self.df_exemplo)
        
        # Criar um DataFrame com um sinal de compra claro
        self.df_sinal_compra = self.df_com_indicadores.copy()
        # Manipular os últimos candles para criar um sinal de compra
        self.df_sinal_compra.loc[self.df_sinal_compra.index[-2], 'close'] = \
            self.df_sinal_compra.loc[self.df_sinal_compra.index[-2], 'bb_lower'] - 0.01  # Fecha abaixo da banda inferior
        self.df_sinal_compra.loc[self.df_sinal_compra.index[-1], 'close'] = \
            self.df_sinal_compra.loc[self.df_sinal_compra.index[-1], 'bb_lower'] + 0.01  # Fecha acima da banda inferior
            
        # Criar um DataFrame com um sinal de venda claro
        self.df_sinal_venda = self.df_com_indicadores.copy()
        # Manipular os últimos candles para criar um sinal de venda
        self.df_sinal_venda.loc[self.df_sinal_venda.index[-2], 'close'] = \
            self.df_sinal_venda.loc[self.df_sinal_venda.index[-2], 'bb_upper'] + 0.01  # Fecha acima da banda superior
        self.df_sinal_venda.loc[self.df_sinal_venda.index[-1], 'close'] = \
            self.df_sinal_venda.loc[self.df_sinal_venda.index[-1], 'bb_upper'] - 0.01  # Fecha abaixo da banda superior

    def test_preparar_dados_para_estrategia(self):
        """
        Testa se a função preparar_dados_para_estrategia adiciona as colunas corretas.
        """
        # Verificar se as colunas de indicadores foram adicionadas
        self.assertIn('bb_upper', self.df_com_indicadores.columns)
        self.assertIn('bb_middle', self.df_com_indicadores.columns)
        self.assertIn('bb_lower', self.df_com_indicadores.columns)
        self.assertIn('adx', self.df_com_indicadores.columns)
        
        # Verificar se não há NaNs nas colunas importantes (exceto as primeiras linhas)
        self.assertFalse(self.df_com_indicadores[['bb_upper', 'bb_middle', 'bb_lower']].iloc[20:].isnull().any().any())

    def test_verificar_sinal_compra(self):
        """
        Testa se a função verificar_sinal_compra identifica corretamente um sinal de compra.
        """
        # Testar com DataFrame que tem sinal de compra
        self.assertTrue(verificar_sinal_compra(self.df_sinal_compra))
        
        # Testar com DataFrame que não tem sinal de compra
        self.assertFalse(verificar_sinal_compra(self.df_com_indicadores))

    def test_verificar_sinal_venda(self):
        """
        Testa se a função verificar_sinal_venda identifica corretamente um sinal de venda.
        """
        # Testar com DataFrame que tem sinal de venda
        self.assertTrue(verificar_sinal_venda(self.df_sinal_venda))
        
        # Testar com DataFrame que não tem sinal de venda
        self.assertFalse(verificar_sinal_venda(self.df_com_indicadores))

    def test_filtrar_mercado_lateralizado(self):
        """
        Testa se a função filtrar_mercado_lateralizado funciona corretamente.
        """
        # Criar DataFrame com ADX baixo (mercado lateralizado)
        df_lateralizado = self.df_com_indicadores.copy()
        df_lateralizado.loc[df_lateralizado.index[-1], 'adx'] = 20  # ADX < 25
        self.assertTrue(filtrar_mercado_lateralizado(df_lateralizado))
        
        # Criar DataFrame com ADX alto (mercado tendencial)
        df_tendencial = self.df_com_indicadores.copy()
        df_tendencial.loc[df_tendencial.index[-1], 'adx'] = 30  # ADX >= 25
        self.assertFalse(filtrar_mercado_lateralizado(df_tendencial))

if __name__ == '__main__':
    unittest.main()