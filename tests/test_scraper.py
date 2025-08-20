"""
抓取器单元测试
使用离线HTML样例进行测试
"""

import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from scraper import ValorHoySource, HistoricoSource, BaseScraper


class TestBaseScraper:
    """测试基础抓取器类"""
    
    def test_parse_rate_value_argentina_format(self):
        """测试阿根廷格式汇率解析"""
        scraper = BaseScraper()
        
        # 测试阿根廷格式：1.292,5000
        result = scraper._parse_rate_value("1.292,5000")
        assert result == 1292.5
        
        # 测试标准格式：1292.50
        result = scraper._parse_rate_value("1292.50")
        assert result == 1292.5
        
        # 测试带空格的格式
        result = scraper._parse_rate_value(" 1.234,5678 ")
        assert result == 1234.5678
        
        # 测试无效值
        result = scraper._parse_rate_value("invalid")
        assert result is None
        
        result = scraper._parse_rate_value("0")
        assert result is None


class TestValorHoySource:
    """测试 ValorHoy 数据源"""
    
    @pytest.fixture
    def sample_html(self):
        """提供样例HTML"""
        return """
        <html>
        <body>
            <div>Fecha: 15/12/2024</div>
            <table>
                <tr>
                    <td>Dolar U.S.A</td>
                    <td>Compra</td>
                    <td>Venta</td>
                </tr>
                <tr>
                    <td></td>
                    <td>1.290,0000</td>
                    <td>1.292,5000</td>
                </tr>
            </table>
        </body>
        </html>
        """
    
    @patch('scraper.requests.Session')
    def test_scrape_success(self, mock_session, sample_html):
        """测试成功抓取"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = sample_html.encode('utf-8')
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # 创建抓取器并测试
        scraper = ValorHoySource()
        result = scraper.scrape()
        
        assert result is not None
        date, rate_sell, source = result
        assert date == "2024-12-15"
        assert rate_sell == 1292.5
        assert source == "bna_divisas_valorhoy"
    
    @patch('scraper.requests.Session')
    def test_scrape_no_date(self, mock_session):
        """测试没有日期信息的情况"""
        html_without_date = """
        <html>
        <body>
            <div>没有日期信息</div>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_without_date.encode('utf-8')
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        scraper = ValorHoySource()
        result = scraper.scrape()
        
        assert result is None
    
    @patch('scraper.requests.Session')
    def test_scrape_no_dollar_row(self, mock_session):
        """测试没有美元行的情况"""
        html_without_dollar = """
        <html>
        <body>
            <div>Fecha: 15/12/2024</div>
            <table>
                <tr>
                    <td>其他货币</td>
                    <td>Compra</td>
                    <td>Venta</td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_without_dollar.encode('utf-8')
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        scraper = ValorHoySource()
        result = scraper.scrape()
        
        assert result is None


class TestHistoricoSource:
    """测试 Historico 数据源"""
    
    @pytest.fixture
    def sample_html(self):
        """提供样例HTML"""
        return """
        <html>
        <body>
            <div>
                <h3>Dolar U.S.A</h3>
                <table>
                    <tr>
                        <td>2024-12-15</td>
                        <td>Compra</td>
                        <td>Venta</td>
                    </tr>
                    <tr>
                        <td>15/12/2024</td>
                        <td>1.290,0000</td>
                        <td>1.292,5000</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
    
    @patch('scraper.requests.Session')
    def test_scrape_success(self, mock_session, sample_html):
        """测试成功抓取"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = sample_html.encode('utf-8')
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # 创建抓取器并测试
        scraper = HistoricoSource()
        result = scraper.scrape("2024-12-15")
        
        assert result is not None
        date, rate_sell, source = result
        assert date == "2024-12-15"
        assert rate_sell == 1292.5
        assert source == "bna_divisas_historico"
    
    @patch('scraper.requests.Session')
    def test_scrape_date_not_found(self, mock_session, sample_html):
        """测试目标日期不存在的情况"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = sample_html.encode('utf-8')
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        scraper = HistoricoSource()
        result = scraper.scrape("2024-12-16")  # 不存在的日期
        
        assert result is None
    
    def test_invalid_date_format(self):
        """测试无效日期格式"""
        scraper = HistoricoSource()
        result = scraper.scrape("invalid-date")
        
        assert result is None


class TestScraperManager:
    """测试抓取器管理器"""
    
    @patch('scraper.ValorHoySource')
    @patch('scraper.HistoricoSource')
    def test_scrape_yesterday_success(self, mock_historico, mock_valorhoy):
        """测试昨天抓取成功"""
        # 模拟 ValorHoy 成功
        mock_valorhoy_instance = Mock()
        mock_valorhoy_instance.scrape.return_value = ("2024-12-15", 1292.5, "bna_divisas_valorhoy")
        mock_valorhoy.return_value = mock_valorhoy_instance
        
        from scraper import ScraperManager
        manager = ScraperManager()
        
        result = manager.scrape_yesterday(fallback=False)
        
        assert result == ("2024-12-15", 1292.5, "bna_divisas_valorhoy")
        mock_valorhoy_instance.scrape.assert_called_once()
        mock_historico_instance = mock_historico.return_value
        mock_historico_instance.scrape.assert_not_called()
    
    @patch('scraper.ValorHoySource')
    @patch('scraper.HistoricoSource')
    def test_scrape_yesterday_with_fallback(self, mock_historico, mock_valorhoy):
        """测试昨天抓取失败后使用备选"""
        # 模拟 ValorHoy 失败，Historico 成功
        mock_valorhoy_instance = Mock()
        mock_valorhoy_instance.scrape.return_value = None
        
        mock_historico_instance = Mock()
        mock_historico_instance.scrape.return_value = ("2024-12-15", 1292.5, "bna_divisas_historico")
        
        mock_valorhoy.return_value = mock_valorhoy_instance
        mock_historico.return_value = mock_historico_instance
        
        from scraper import ScraperManager
        manager = ScraperManager()
        
        result = manager.scrape_yesterday(fallback=True)
        
        assert result == ("2024-12-15", 1292.5, "bna_divisas_historico")
        mock_valorhoy_instance.scrape.assert_called_once()
        mock_historico_instance.scrape.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
