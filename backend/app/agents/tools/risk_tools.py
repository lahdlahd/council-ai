"""
Risk Management Tools
Portfolio risk assessment, position sizing, drawdown management, veto enforcement

Production-grade with risk controls and position limit calculations
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk classification"""
    CRITICAL = "critical"      # > 3% portfolio loss possible
    HIGH = "high"              # 2-3% portfolio loss possible
    MEDIUM = "medium"          # 1-2% portfolio loss possible
    LOW = "low"                # 0.5-1% portfolio loss possible
    MINIMAL = "minimal"        # < 0.5% portfolio loss possible


class ExposureLevel(str, Enum):
    """Portfolio exposure levels"""
    FULL = "full"              # 100% allocated
    HIGH = "high"              # 75-99% allocated
    MODERATE = "moderate"      # 50-74% allocated
    LOW = "low"                # 25-49% allocated
    MINIMAL = "minimal"        # < 25% allocated


class RiskTools:
    """Suite of risk management tools"""
    
    @staticmethod
    def calculate_value_at_risk(
        returns: List[float],
        position_size: float,
        confidence_level: float = 0.95
    ) -> Dict[str, float]:
        """
        Calculate Value at Risk (VaR)
        
        VaR = percentile of losses at confidence level
        Example: 95% VaR = worst loss in 19 out of 20 days
        
        Args:
            returns: Historical daily returns
            position_size: Position size in USD
            confidence_level: Confidence level (0.95 = 95%)
        
        Returns:
            Dict with var_amount, var_pct, expected_shortfall
        """
        try:
            if len(returns) < 10:
                return {
                    "var_amount": position_size * 0.02,  # Assume 2% default
                    "var_pct": 0.02,
                    "expected_shortfall": 0.025,
                    "confidence_level": confidence_level
                }
            
            returns_arr = np.array(returns, dtype=float)
            
            # Calculate percentile loss
            percentile_idx = int((1 - confidence_level) * 100)
            var_pct = np.percentile(returns_arr, percentile_idx)
            
            # Ensure it's a loss (negative)
            if var_pct > 0:
                var_pct = 0.0
            
            var_pct = abs(var_pct)  # Convert to positive loss
            var_amount = position_size * var_pct
            
            # Expected shortfall (average of worst losses)
            worst_returns = returns_arr[returns_arr <= -var_pct]
            if len(worst_returns) > 0:
                expected_shortfall = abs(np.mean(worst_returns))
            else:
                expected_shortfall = var_pct
            
            return {
                "var_amount": float(var_amount),
                "var_pct": float(var_pct),
                "expected_shortfall": float(expected_shortfall),
                "confidence_level": float(confidence_level)
            }
            
        except Exception as e:
            logger.error(f"VaR calculation failed: {e}")
            return {
                "var_amount": position_size * 0.02,
                "var_pct": 0.02,
                "expected_shortfall": 0.025,
                "confidence_level": confidence_level
            }
    
    @staticmethod
    def calculate_position_size(
        account_size: float,
        volatility: float,
        max_risk_pct: float = 0.02,
        risk_free_rate: float = 0.02
    ) -> Dict[str, float]:
        """
        Calculate optimal position size using Kelly Criterion variant
        
        Adjusts position size inversely to volatility
        
        Args:
            account_size: Total account balance
            volatility: Annualized volatility
            max_risk_pct: Maximum risk per trade (default 2%)
            risk_free_rate: Annual risk-free rate
        
        Returns:
            Dict with position_size, kelly_fraction, volatility_adjusted_size
        """
        try:
            if volatility == 0:
                volatility = 0.1  # Default 10% if no volatility
            
            # Kelly criterion: f = (return - risk_free) / volatility²
            # For position sizing: Size inversely proportional to volatility
            kelly_fraction = max_risk_pct / (volatility ** 2)
            kelly_fraction = min(kelly_fraction, 1.0)  # Cap at 100%
            
            # Base position size
            position_size = account_size * kelly_fraction
            
            # Volatility adjustment (reduce position in high volatility)
            vol_adjustment = 1.0 / (1.0 + volatility)
            volatility_adjusted_size = position_size * vol_adjustment
            
            # Further limit to max risk amount
            max_position_by_risk = account_size * max_risk_pct / 0.02  # Assume 2% stop loss
            final_position_size = min(volatility_adjusted_size, max_position_by_risk)
            
            return {
                "position_size": float(final_position_size),
                "kelly_fraction": float(kelly_fraction),
                "volatility_adjusted_size": float(volatility_adjusted_size),
                "account_size": float(account_size),
                "volatility": float(volatility)
            }
            
        except Exception as e:
            logger.error(f"Position size calculation failed: {e}")
            return {
                "position_size": account_size * 0.05,  # Default 5%
                "kelly_fraction": 0.05,
                "volatility_adjusted_size": account_size * 0.05,
                "account_size": account_size,
                "volatility": volatility
            }
    
    @staticmethod
    def assess_portfolio_concentration(
        current_holdings: Dict[str, float],
        account_size: float
    ) -> Dict[str, any]:
        """
        Assess portfolio concentration risk
        
        Args:
            current_holdings: Dict of {symbol: position_value}
            account_size: Total account size
        
        Returns:
            Dict with concentration_score, largest_position, diversification_score
        """
        try:
            if not current_holdings or account_size == 0:
                return {
                    "concentration_score": 0.0,
                    "largest_position_pct": 0.0,
                    "diversification_score": 1.0,
                    "herfindahl_index": 0.0,
                    "num_holdings": 0,
                    "recommendation": "No positions"
                }
            
            # Calculate allocation percentages
            allocations = []
            for symbol, value in current_holdings.items():
                pct = value / account_size if account_size > 0 else 0
                allocations.append(pct)
            
            allocations = np.array(allocations)
            
            # Herfindahl-Hirschman Index (HHI)
            # HHI = Σ(allocation%)²
            # Perfect diversification: HHI = 1/n
            # Extreme concentration: HHI = 1.0
            herfindahl = np.sum(allocations ** 2)
            
            # Perfect diversification benchmark for this many assets
            perfect_hhi = 1.0 / len(allocations) if len(allocations) > 0 else 1.0
            
            # Diversification score (0-1, where 1 = perfect)
            if herfindahl > 0:
                diversification_score = perfect_hhi / herfindahl
            else:
                diversification_score = 0.0
            
            diversification_score = min(diversification_score, 1.0)
            
            # Concentration score (opposite of diversification)
            concentration_score = 1.0 - diversification_score
            
            # Largest position
            largest_position_pct = float(np.max(allocations)) if len(allocations) > 0 else 0.0
            
            # Recommendation
            if concentration_score > 0.4:
                recommendation = "High concentration - reduce largest position"
            elif concentration_score > 0.25:
                recommendation = "Moderate concentration - acceptable"
            else:
                recommendation = "Well diversified"
            
            return {
                "concentration_score": float(concentration_score),
                "largest_position_pct": largest_position_pct,
                "diversification_score": float(diversification_score),
                "herfindahl_index": float(herfindahl),
                "num_holdings": len(allocations),
                "recommendation": recommendation
            }
            
        except Exception as e:
            logger.error(f"Concentration assessment failed: {e}")
            return {
                "concentration_score": 0.5,
                "largest_position_pct": 0.0,
                "diversification_score": 0.5,
                "herfindahl_index": 0.0,
                "num_holdings": 0,
                "recommendation": "Analysis failed"
            }
    
    @staticmethod
    def calculate_drawdown_limit(
        account_size: float,
        daily_vol: float,
        max_daily_loss_pct: float = 0.01,
        max_weekly_loss_pct: float = 0.03,
        max_monthly_loss_pct: float = 0.05
    ) -> Dict[str, float]:
        """
        Calculate drawdown limits and stop-loss levels
        
        Args:
            account_size: Current account size
            daily_vol: Daily volatility
            max_daily_loss_pct: Maximum daily loss %
            max_weekly_loss_pct: Maximum weekly loss %
            max_monthly_loss_pct: Maximum monthly loss %
        
        Returns:
            Dict with daily_limit, weekly_limit, monthly_limit, stop_all_trading_level
        """
        try:
            daily_limit = account_size * max_daily_loss_pct
            weekly_limit = account_size * max_weekly_loss_pct
            monthly_limit = account_size * max_monthly_loss_pct
            
            # Stop-all-trading level (accumulated losses)
            stop_all_trading_level = account_size * (max_monthly_loss_pct * 2)  # Double monthly limit
            
            # Volatility-adjusted limits
            vol_factor = 1.0 + daily_vol * 10  # Higher vol = higher limits
            adjusted_daily = daily_limit * vol_factor
            
            return {
                "daily_limit": float(daily_limit),
                "weekly_limit": float(weekly_limit),
                "monthly_limit": float(monthly_limit),
                "stop_all_trading_level": float(stop_all_trading_level),
                "volatility_adjusted_daily": float(adjusted_daily),
                "daily_volatility": float(daily_vol)
            }
            
        except Exception as e:
            logger.error(f"Drawdown limit calculation failed: {e}")
            return {
                "daily_limit": account_size * 0.01,
                "weekly_limit": account_size * 0.03,
                "monthly_limit": account_size * 0.05,
                "stop_all_trading_level": account_size * 0.10,
                "volatility_adjusted_daily": account_size * 0.01,
                "daily_volatility": 0.0
            }
    
    @staticmethod
    def assess_correlation_risk(
        correlations: Dict[str, float],
        holdings: List[str],
        threshold: float = 0.7
    ) -> Dict[str, any]:
        """
        Assess risk from correlated positions
        
        Args:
            correlations: Dict of {pair: correlation_coefficient}
            holdings: List of symbols held
            threshold: High correlation threshold (default 0.7)
        
        Returns:
            Dict with correlation_risk, high_correlations, diversification_breakdown
        """
        try:
            if not holdings:
                return {
                    "correlation_risk": 0.0,
                    "high_correlation_count": 0,
                    "average_correlation": 0.0,
                    "max_correlation": 0.0,
                    "high_correlations": [],
                    "risk_level": RiskLevel.MINIMAL.value
                }
            
            high_correlations = []
            valid_correlations = []
            
            for pair, corr in correlations.items():
                if abs(corr) > threshold:
                    high_correlations.append({
                        "pair": pair,
                        "correlation": float(corr),
                        "diversification_benefit": "Low"
                    })
            
            valid_correlations = [abs(c) for c in correlations.values() if c is not None]
            
            # Calculate risk metrics
            avg_correlation = np.mean(valid_correlations) if valid_correlations else 0.0
            max_correlation = np.max(valid_correlations) if valid_correlations else 0.0
            
            # Correlation risk (0-1 scale)
            correlation_risk = (avg_correlation + max_correlation) / 2
            
            # Risk level
            if correlation_risk > 0.8:
                risk_level = RiskLevel.CRITICAL.value
            elif correlation_risk > 0.6:
                risk_level = RiskLevel.HIGH.value
            elif correlation_risk > 0.4:
                risk_level = RiskLevel.MEDIUM.value
            else:
                risk_level = RiskLevel.LOW.value
            
            return {
                "correlation_risk": float(correlation_risk),
                "high_correlation_count": len(high_correlations),
                "average_correlation": float(avg_correlation),
                "max_correlation": float(max_correlation),
                "high_correlations": high_correlations,
                "risk_level": risk_level
            }
            
        except Exception as e:
            logger.error(f"Correlation risk assessment failed: {e}")
            return {
                "correlation_risk": 0.5,
                "high_correlation_count": 0,
                "average_correlation": 0.0,
                "max_correlation": 0.0,
                "high_correlations": [],
                "risk_level": RiskLevel.MEDIUM.value
            }
    
    @staticmethod
    def calculate_stress_test(
        current_prices: Dict[str, float],
        positions: Dict[str, float],
        stress_scenarios: List[float] = None
    ) -> Dict[str, any]:
        """
        Stress test portfolio against price movements
        
        Args:
            current_prices: Dict of {symbol: current_price}
            positions: Dict of {symbol: quantity_held}
            stress_scenarios: List of price movements to test (default: [-0.10, -0.20, -0.30])
        
        Returns:
            Dict with stress_test_results for each scenario
        """
        try:
            if stress_scenarios is None:
                stress_scenarios = [-0.10, -0.20, -0.30]  # -10%, -20%, -30%
            
            portfolio_value = 0.0
            results = {}
            
            # Current portfolio value
            for symbol, quantity in positions.items():
                current_price = current_prices.get(symbol, 0.0)
                portfolio_value += current_price * quantity
            
            # Stress test each scenario
            for scenario_loss in stress_scenarios:
                scenario_value = 0.0
                
                for symbol, quantity in positions.items():
                    current_price = current_prices.get(symbol, 0.0)
                    stressed_price = current_price * (1 + scenario_loss)
                    scenario_value += stressed_price * quantity
                
                loss_amount = portfolio_value - scenario_value
                loss_pct = loss_amount / portfolio_value if portfolio_value > 0 else 0.0
                
                results[f"scenario_{abs(scenario_loss):.0%}"] = {
                    "portfolio_value": float(scenario_value),
                    "loss_amount": float(loss_amount),
                    "loss_pct": float(loss_pct),
                    "remaining_capital": float(scenario_value)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Stress test failed: {e}")
            return {}
    
    @staticmethod
    def calculate_overall_risk_score(
        volatility: float,
        max_drawdown: float,
        concentration_score: float,
        correlation_risk: float,
        position_sizing_ratio: float
    ) -> Dict[str, any]:
        """
        Calculate overall portfolio risk score (0-100)
        
        Args:
            volatility: Annual volatility (e.g., 0.25 for 25%)
            max_drawdown: Historical max drawdown (e.g., -0.15 for -15%)
            concentration_score: Concentration score (0-1)
            correlation_risk: Correlation risk (0-1)
            position_sizing_ratio: Actual size / optimal size (1.0 = optimal)
        
        Returns:
            Dict with overall_risk_score, risk_level, component_scores
        """
        try:
            # Component scores (normalize to 0-100)
            volatility_score = min(volatility * 100, 100)  # Higher vol = higher risk
            drawdown_score = abs(max_drawdown) * 100  # Higher drawdown = higher risk
            concentration_risk_score = concentration_score * 100
            correlation_risk_score = correlation_risk * 100
            sizing_risk_score = abs(position_sizing_ratio - 1.0) * 50  # Deviation from optimal
            
            # Weighted average
            overall_risk = (
                volatility_score * 0.25 +
                drawdown_score * 0.30 +
                concentration_risk_score * 0.20 +
                correlation_risk_score * 0.15 +
                sizing_risk_score * 0.10
            )
            
            overall_risk = min(overall_risk, 100)
            
            # Risk level classification
            if overall_risk > 75:
                risk_level = RiskLevel.CRITICAL.value
            elif overall_risk > 60:
                risk_level = RiskLevel.HIGH.value
            elif overall_risk > 40:
                risk_level = RiskLevel.MEDIUM.value
            elif overall_risk > 20:
                risk_level = RiskLevel.LOW.value
            else:
                risk_level = RiskLevel.MINIMAL.value
            
            # Veto decision logic
            should_veto = overall_risk > 75
            veto_reason = ""
            if should_veto:
                if drawdown_score > 40:
                    veto_reason = "Historical drawdown exceeds acceptable limits"
                elif concentration_risk_score > 70:
                    veto_reason = "Portfolio concentration too high"
                elif volatility_score > 80:
                    veto_reason = "Volatility exceeds risk tolerance"
                else:
                    veto_reason = "Overall risk score exceeds limits"
            
            return {
                "overall_risk_score": float(overall_risk),
                "risk_level": risk_level,
                "should_veto": should_veto,
                "veto_reason": veto_reason,
                "component_scores": {
                    "volatility": float(volatility_score),
                    "drawdown": float(drawdown_score),
                    "concentration": float(concentration_risk_score),
                    "correlation": float(correlation_risk_score),
                    "position_sizing": float(sizing_risk_score)
                }
            }
            
        except Exception as e:
            logger.error(f"Overall risk score calculation failed: {e}")
            return {
                "overall_risk_score": 50.0,
                "risk_level": RiskLevel.MEDIUM.value,
                "should_veto": False,
                "veto_reason": "",
                "component_scores": {}
            }
    
    @staticmethod
    def validate_position_limits(
        proposed_position: float,
        account_size: float,
        current_allocation_pct: float,
        max_single_position_pct: float = 0.15
    ) -> Dict[str, any]:
        """
        Validate if proposed position respects limits
        
        Args:
            proposed_position: Size of proposed position
            account_size: Total account size
            current_allocation_pct: Current allocation % (0-1)
            max_single_position_pct: Max allowed position % (default 15%)
        
        Returns:
            Dict with is_valid, proposed_pct, max_allowed, adjustment
        """
        try:
            proposed_pct = proposed_position / account_size if account_size > 0 else 0
            new_total_pct = current_allocation_pct + proposed_pct
            
            # Check limits
            position_limit_ok = proposed_pct <= max_single_position_pct
            total_allocation_ok = new_total_pct <= 1.0
            
            is_valid = position_limit_ok and total_allocation_ok
            
            # Calculate adjustment if needed
            if not position_limit_ok:
                adjusted_position = account_size * max_single_position_pct
                adjustment = adjusted_position / proposed_position if proposed_position > 0 else 1.0
            elif not total_allocation_ok:
                remaining_room = (1.0 - current_allocation_pct) * account_size
                adjusted_position = remaining_room
                adjustment = adjusted_position / proposed_position if proposed_position > 0 else 1.0
            else:
                adjusted_position = proposed_position
                adjustment = 1.0
            
            return {
                "is_valid": is_valid,
                "proposed_pct": float(proposed_pct),
                "new_total_pct": float(new_total_pct),
                "max_allowed_single_pct": float(max_single_position_pct),
                "position_limit_ok": position_limit_ok,
                "total_allocation_ok": total_allocation_ok,
                "adjusted_position": float(adjusted_position),
                "adjustment_ratio": float(adjustment)
            }
            
        except Exception as e:
            logger.error(f"Position limit validation failed: {e}")
            return {
                "is_valid": False,
                "proposed_pct": 0.0,
                "new_total_pct": 0.0,
                "max_allowed_single_pct": 0.15,
                "position_limit_ok": False,
                "total_allocation_ok": False,
                "adjusted_position": 0.0,
                "adjustment_ratio": 0.0
            }
