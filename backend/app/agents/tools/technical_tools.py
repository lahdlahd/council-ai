"""
Technical Analysis Tools
Implementations of RSI, MACD, EMA, volume analysis, support/resistance, and trend identification.
Production-grade with error handling and validation.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Suite of technical analysis indicators"""
    
    @staticmethod
    def calculate_rsi(closes: List[float], period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI)
        
        RSI = 100 - (100 / (1 + RS))
        RS = Average Gain / Average Loss
        
        Args:
            closes: List of closing prices
            period: Period for calculation (default 14)
        
        Returns:
            RSI value 0-100
        """
        if len(closes) < period + 1:
            raise ValueError(f"Need at least {period + 1} closes, got {len(closes)}")
        
        closes = np.array(closes, dtype=float)
        deltas = np.diff(closes)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gain and loss
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(np.clip(rsi, 0, 100))
    
    @staticmethod
    def calculate_macd(
        closes: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, float]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            closes: List of closing prices
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line EMA period (default 9)
        
        Returns:
            Dict with keys: 'value', 'signal', 'histogram'
        """
        if len(closes) < slow_period:
            raise ValueError(f"Need at least {slow_period} closes, got {len(closes)}")
        
        closes = np.array(closes, dtype=float)
        
        # Calculate EMAs
        ema_fast = TechnicalIndicators.calculate_ema(closes.tolist(), fast_period)
        ema_slow = TechnicalIndicators.calculate_ema(closes.tolist(), slow_period)
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        # Need to recalculate MACD for all points for signal line
        macd_values = []
        for i in range(slow_period - 1, len(closes)):
            ema_f = TechnicalIndicators.calculate_ema(closes[:i+1].tolist(), fast_period)
            ema_s = TechnicalIndicators.calculate_ema(closes[:i+1].tolist(), slow_period)
            macd_values.append(ema_f - ema_s)
        
        # Signal line
        if len(macd_values) < signal_period:
            signal_line = np.mean(macd_values)
        else:
            signal_line = TechnicalIndicators.calculate_ema(
                macd_values[-signal_period:],
                signal_period
            )
        
        histogram = macd_line - signal_line
        
        return {
            "value": float(macd_line),
            "signal": float(signal_line),
            "histogram": float(histogram)
        }
    
    @staticmethod
    def calculate_ema(closes: List[float], period: int) -> float:
        """
        Calculate Exponential Moving Average (EMA)
        
        EMA = (Close - EMA_prev) × multiplier + EMA_prev
        multiplier = 2 / (period + 1)
        
        Args:
            closes: List of closing prices
            period: EMA period
        
        Returns:
            EMA value
        """
        if len(closes) < period:
            raise ValueError(f"Need at least {period} closes, got {len(closes)}")
        
        closes = np.array(closes, dtype=float)
        
        # Start with SMA for first EMA value
        sma = np.mean(closes[:period])
        
        multiplier = 2.0 / (period + 1)
        ema = sma
        
        # Calculate EMA for each subsequent price
        for i in range(period, len(closes)):
            ema = (closes[i] - ema) * multiplier + ema
        
        return float(ema)
    
    @staticmethod
    def calculate_bollinger_bands(
        closes: List[float],
        period: int = 20,
        num_std: float = 2.0
    ) -> Dict[str, float]:
        """
        Calculate Bollinger Bands
        
        Args:
            closes: List of closing prices
            period: SMA period
            num_std: Number of standard deviations
        
        Returns:
            Dict with keys: 'upper', 'middle', 'lower'
        """
        if len(closes) < period:
            raise ValueError(f"Need at least {period} closes, got {len(closes)}")
        
        closes = np.array(closes[-period:], dtype=float)
        
        middle = np.mean(closes)
        std = np.std(closes)
        
        return {
            "upper": float(middle + (std * num_std)),
            "middle": float(middle),
            "lower": float(middle - (std * num_std))
        }
    
    @staticmethod
    def analyze_volume_trend(
        volumes: List[float],
        closes: List[float],
        period: int = 20
    ) -> Dict[str, any]:
        """
        Analyze volume trend
        
        Args:
            volumes: List of volumes
            closes: List of closing prices
            period: Period for averaging
        
        Returns:
            Dict with trend direction and strength
        """
        if len(volumes) < period:
            raise ValueError(f"Need at least {period} data points")
        
        volumes = np.array(volumes[-period:], dtype=float)
        closes = np.array(closes[-period:], dtype=float)
        
        # Average volume
        avg_volume = np.mean(volumes)
        current_volume = volumes[-1]
        
        # Volume trend
        volume_trend = "increasing" if current_volume > avg_volume else "decreasing"
        volume_strength = abs(current_volume - avg_volume) / avg_volume
        
        # Volume-weighted price changes
        price_changes = np.diff(closes)
        on_balance_volume = np.sum(
            np.where(price_changes > 0, volumes[1:], -volumes[1:])
        )
        
        return {
            "trend": volume_trend,
            "strength": float(np.clip(volume_strength, 0, 2.0)),
            "current_volume": float(current_volume),
            "average_volume": float(avg_volume),
            "on_balance_volume": float(on_balance_volume)
        }
    
    @staticmethod
    def identify_trend(closes: List[float], period: int = 20) -> Dict[str, any]:
        """
        Identify price trend using simple comparison
        
        Args:
            closes: List of closing prices
            period: Period for trend analysis
        
        Returns:
            Dict with trend direction and strength
        """
        if len(closes) < period:
            raise ValueError(f"Need at least {period} closes")
        
        closes = np.array(closes[-period:], dtype=float)
        
        # Calculate linear regression slope
        x = np.arange(len(closes))
        slope = np.polyfit(x, closes, 1)[0]
        
        # Normalize slope
        avg_price = np.mean(closes)
        normalized_slope = (slope / avg_price) * 100 if avg_price > 0 else 0
        
        # Determine direction
        if normalized_slope > 0.5:
            direction = "UP"
        elif normalized_slope < -0.5:
            direction = "DOWN"
        else:
            direction = "SIDEWAYS"
        
        # Strength (0-1 scale)
        strength = min(abs(normalized_slope) / 2.0, 1.0)
        
        return {
            "direction": direction,
            "strength": float(strength),
            "slope": float(slope)
        }
    
    @staticmethod
    def find_support_resistance(
        closes: List[float],
        highs: List[float],
        lows: List[float],
        lookback: int = 50
    ) -> Dict[str, List[float]]:
        """
        Find support and resistance levels
        
        Uses pivot point analysis and local extrema detection
        
        Args:
            closes: List of closing prices
            highs: List of high prices
            lows: List of low prices
            lookback: Period to analyze
        
        Returns:
            Dict with 'support' and 'resistance' level lists
        """
        if len(closes) < lookback:
            lookback = len(closes)
        
        closes = np.array(closes[-lookback:], dtype=float)
        highs = np.array(highs[-lookback:], dtype=float)
        lows = np.array(lows[-lookback:], dtype=float)
        
        # Find local maxima (resistance)
        resistance = []
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                resistance.append(float(highs[i]))
        
        # Find local minima (support)
        support = []
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                support.append(float(lows[i]))
        
        # Calculate pivot levels
        high = np.max(highs)
        low = np.min(lows)
        close = closes[-1]
        
        pivot = (high + low + close) / 3
        resistance.append(pivot * 1.1)
        support.append(pivot * 0.9)
        
        # Remove duplicates and sort
        resistance = sorted(list(set(np.round(resistance, 2))))
        support = sorted(list(set(np.round(support, 2))), reverse=True)
        
        return {
            "support": support[:3] if support else [],  # Top 3
            "resistance": resistance[-3:] if resistance else []  # Top 3
        }
    
    @staticmethod
    def detect_divergence(
        closes: List[float],
        highs: List[float],
        lows: List[float],
        rsi_values: List[float],
        period: int = 20
    ) -> Dict[str, any]:
        """
        Detect RSI divergences (potential reversals)
        
        Args:
            closes: List of closing prices
            highs: List of highs
            lows: List of lows
            rsi_values: List of RSI values
            period: Period to check
        
        Returns:
            Dict with divergence information
        """
        if len(closes) < period or len(rsi_values) < period:
            return {"divergence": None, "strength": 0.0}
        
        closes_recent = closes[-period:]
        rsi_recent = rsi_values[-period:]
        
        # Check for bullish divergence (price lower, RSI higher)
        # Check for bearish divergence (price higher, RSI lower)
        
        price_trend = "up" if closes_recent[-1] > closes_recent[0] else "down"
        rsi_trend = "up" if rsi_recent[-1] > rsi_recent[0] else "down"
        
        divergence_type = None
        if price_trend == "down" and rsi_trend == "up":
            divergence_type = "bullish"
        elif price_trend == "up" and rsi_trend == "down":
            divergence_type = "bearish"
        
        strength = abs(rsi_recent[-1] - rsi_recent[0]) / 100.0 if divergence_type else 0.0
        
        return {
            "divergence": divergence_type,
            "strength": float(strength)
        }
    
    @staticmethod
    def identify_candlestick_pattern(
        opens: List[float],
        highs: List[float],
        lows: List[float],
        closes: List[float]
    ) -> str:
        """
        Identify candlestick patterns (simplified)
        
        Returns pattern name if found
        """
        if len(closes) < 2:
            return "INSUFFICIENT_DATA"
        
        # Last candle properties
        open_price = opens[-1]
        high_price = highs[-1]
        low_price = lows[-1]
        close_price = closes[-1]
        
        body = abs(close_price - open_price)
        range_price = high_price - low_price
        
        # Doji (small body, long wicks)
        if body < range_price * 0.1 and range_price > range_price * 0.5:
            return "DOJI"
        
        # Hammer (small body, long lower wick, bullish)
        if close_price > open_price and body < range_price * 0.3:
            lower_wick = open_price - low_price
            if lower_wick > range_price * 0.5:
                return "HAMMER"
        
        # Shooting Star (small body, long upper wick, bearish)
        if close_price < open_price and body < range_price * 0.3:
            upper_wick = high_price - open_price
            if upper_wick > range_price * 0.5:
                return "SHOOTING_STAR"
        
        # Engulfing (today's body engulfs yesterday's)
        if len(closes) >= 2:
            prev_open = opens[-2]
            prev_close = closes[-2]
            prev_body = abs(prev_close - prev_open)
            
            if body > prev_body * 1.5:
                if close_price > open_price and close_price > prev_close and open_price < prev_open:
                    return "BULLISH_ENGULFING"
                elif close_price < open_price and close_price < prev_close and open_price > prev_open:
                    return "BEARISH_ENGULFING"
        
        # Default
        if close_price > open_price:
            return "BULLISH_CANDLE"
        else:
            return "BEARISH_CANDLE"
