import Foundation

struct MilesValue {
    let low: Double
    let high: Double
}

func calculateMilesValue(miles: Double) -> MilesValue {
    return MilesValue(low: miles * Valuations.mileValueLow,
                      high: miles * Valuations.mileValueHigh)
}

func formatCurrency(_ value: Double) -> String {
    let formatter = NumberFormatter()
    formatter.numberStyle = .currency
    formatter.locale = .current
    return formatter.string(from: NSNumber(value: value)) ?? "$0.00"
}

// MARK: - Award Accelerator

struct AcceleratorResult {
    let milesWorthLow: Double
    let milesWorthHigh: Double
    let costPerMile: Double
    let pqpCostLow: Double?
    let pqpCostHigh: Double?
    let verdict: String
    let cpm: Double
}

func evaluateAccelerator(miles: Double, pqp: Double, cost: Double) -> AcceleratorResult? {
    guard miles >= 0, cost >= 0, pqp >= 0 else { return nil }

    let value = calculateMilesValue(miles: miles)
    let costPerMile = miles > 0 ? cost / miles : .infinity

    let effectiveCostLow = pqp > 0 ? (cost - value.high) : cost
    let effectiveCostHigh = pqp > 0 ? (cost - value.low) : cost

    var verdict: String
    var pqpCostLow: Double? = nil
    var pqpCostHigh: Double? = nil

    if pqp > 0 {
        pqpCostLow = effectiveCostLow / pqp
        pqpCostHigh = effectiveCostHigh / pqp

        if let pqpCostLow { // mirror Python logic
            if pqpCostLow < 1.30 {
                verdict = "✅ Excellent Deal!"
            } else if pqpCostLow < 1.50 {
                verdict = "🟡 Decent Value."
            } else {
                verdict = "❌ Not Worth It."
            }
        } else {
            verdict = "❌ Not Worth It."
        }
    } else {
        if costPerMile < 0.01 {
            verdict = "✅ Good Deal!"
        } else if costPerMile < Valuations.mileValueLow {
            verdict = "🟡 Decent Value."
        } else {
            verdict = "❌ Not Worth It."
        }
    }

    return AcceleratorResult(
        milesWorthLow: value.low,
        milesWorthHigh: value.high,
        costPerMile: costPerMile.isFinite ? costPerMile : 0,
        pqpCostLow: pqpCostLow,
        pqpCostHigh: pqpCostHigh,
        verdict: verdict,
        cpm: (miles > 0) ? (cost / miles) * 100.0 : 0
    )
}

// MARK: - Upgrade Offer

private func isUpgradeNotWorthIt(
    travelHours: Int,
    cashUpgrade: Double,
    fullFare: Double,
    miles: Double,
    cashCost: Double,
    fromClass: CabinClass,
    toClass: CabinClass,
    originalFullFare: Double
) -> String? {
    if travelHours < Valuations.upgradeComfortHours && fromClass == .economy && toClass == .premiumPlus {
        return "⚠️ Short flight – upgrade may not be worth it."
    }
    if cashUpgrade > 0.8 * fullFare && originalFullFare > 0 {
        return "⚠️ Upgrade cost is too close to full fare price."
    }
    if (miles > 0 && cashCost > 0) && (cashCost + (miles * Valuations.mileValueLow) > fullFare) && fullFare > 0 {
        return "⚠️ Miles + Cash upgrade is costing more than a full-fare business class ticket."
    }
    if fromClass == .premiumPlus && toClass == .business && travelHours < 5 {
        return "⚠️ Small difference in comfort for this flight length – not worth upgrading."
    }
    return nil
}

struct UpgradeResult {
    let milesWorthLow: Double
    let milesWorthHigh: Double
    let totalMilesCashUpgradeLow: Double?
    let totalMilesCashUpgradeHigh: Double?
    let totalCashUpgrade: Double
    let fullFarePrice: Double
    let savingsMilesCashLow: Double?
    let savingsMilesCashHigh: Double?
    let savingsCashUpgrade: Double
    let bestOption: String
    let verdict: String
    let warning: String?
    let comfortFactor: Double
}

func evaluateUpgrade(
    miles: Double,
    cashCost: Double,
    fullCashUpgrade: Double,
    fullFareCost: Double,
    travelHours: Int,
    fromClass: CabinClass,
    toClass: CabinClass
) -> UpgradeResult? {
    guard miles >= 0, cashCost >= 0, fullCashUpgrade >= 0, fullFareCost >= 0 else { return nil }

    if fromClass == toClass {
        return UpgradeResult(
            milesWorthLow: 0, milesWorthHigh: 0,
            totalMilesCashUpgradeLow: nil, totalMilesCashUpgradeHigh: nil,
            totalCashUpgrade: 0, fullFarePrice: 0,
            savingsMilesCashLow: nil, savingsMilesCashHigh: nil,
            savingsCashUpgrade: 0,
            bestOption: "None",
            verdict: "ℹ️ No upgrade selected",
            warning: "⚠️ You've selected the same cabin class for both options. No upgrade needed.",
            comfortFactor: 1.0
        )
    }

    let comfortFactor = 1.0 + (0.05 * Double(travelHours))
    let upgradeMultiplier = UpgradeMultipliers.multiplier(from: fromClass, to: toClass)

    let originalFullFare = fullFareCost
    var deemedFullFare = fullFareCost
    if deemedFullFare == 0 {
        deemedFullFare = max(fullCashUpgrade * 1.5, 1000)
    }

    var milesVar = miles
    var cashVar = cashCost
    if milesVar == 0 && cashVar == 0 {
        milesVar = 0
        cashVar = fullCashUpgrade
    }

    let milesValue = calculateMilesValue(miles: milesVar)
    let totalMilesCashLow = milesVar > 0 ? (cashVar + milesValue.low) : nil
    let totalMilesCashHigh = milesVar > 0 ? (cashVar + milesValue.high) : nil

    var totalCashOnly = fullCashUpgrade
    if totalCashOnly == 0 { totalCashOnly = deemedFullFare }

    let savingsLow = (deemedFullFare - (totalMilesCashHigh ?? deemedFullFare)) * comfortFactor * upgradeMultiplier
    let savingsHigh = (deemedFullFare - (totalMilesCashLow ?? deemedFullFare)) * comfortFactor * upgradeMultiplier
    let savingsCash = (deemedFullFare - totalCashOnly) * comfortFactor * upgradeMultiplier

    let bestOption: String
    if savingsHigh > savingsCash && savingsHigh > 0 {
        bestOption = "Miles + Cash"
    } else if savingsCash > 0 {
        bestOption = "Cash Upgrade"
    } else {
        bestOption = "Buy Full Fare Ticket"
    }

    let verdict = "✅ Best Option: \(bestOption)"
    let warning = isUpgradeNotWorthIt(
        travelHours: travelHours,
        cashUpgrade: totalCashOnly,
        fullFare: deemedFullFare,
        miles: milesVar,
        cashCost: cashVar,
        fromClass: fromClass,
        toClass: toClass,
        originalFullFare: originalFullFare
    )

    return UpgradeResult(
        milesWorthLow: milesValue.low,
        milesWorthHigh: milesValue.high,
        totalMilesCashUpgradeLow: totalMilesCashLow,
        totalMilesCashUpgradeHigh: totalMilesCashHigh,
        totalCashUpgrade: totalCashOnly,
        fullFarePrice: deemedFullFare,
        savingsMilesCashLow: totalMilesCashLow != nil ? savingsLow : nil,
        savingsMilesCashHigh: totalMilesCashHigh != nil ? savingsHigh : nil,
        savingsCashUpgrade: savingsCash,
        bestOption: bestOption,
        verdict: verdict,
        warning: warning,
        comfortFactor: comfortFactor
    )
}

// MARK: - Ticket Purchase Comparison

struct PurchaseComparisonResult {
    let milesCashValueLow: Double
    let milesCashValueHigh: Double
    let totalCostMilesLow: Double
    let totalCostMilesHigh: Double
    let totalCostMixedLow: Double?
    let totalCostMixedHigh: Double?
    let totalCostCash: Double
    let cpmMiles: Double
    let cpmMixed: Double?
    let bestOption: String
    let verdict: String
    let advice: String?
}

func evaluateBestOption(
    milesPrice: Double,
    cashPrice: Double,
    milesPlusCashMiles: Double,
    milesPlusCashCash: Double
) -> PurchaseComparisonResult {
    let milesValue = calculateMilesValue(miles: milesPrice)
    let mixedValue = calculateMilesValue(miles: milesPlusCashMiles)

    let totalCostMilesLow = milesValue.low
    let totalCostMilesHigh = milesValue.high

    let validMixed = milesPlusCashMiles > 0 && milesPlusCashCash > 0
    let totalCostMixedLow = validMixed ? (mixedValue.low + milesPlusCashCash) : nil
    let totalCostMixedHigh = validMixed ? (mixedValue.high + milesPlusCashCash) : nil

    var options: [(String, Double)] = [("Cash", cashPrice), ("Miles", totalCostMilesLow)]
    if let totalCostMixedLow { options.append(("Miles + Cash", totalCostMixedLow)) }

    let bestOption = options.min(by: { $0.1 < $1.1 })?.0 ?? "Cash"

    let cpmMiles = milesPrice > 0 ? (cashPrice / milesPrice) * 100.0 : 0
    let cpmMixed = (milesPlusCashMiles > 0) ? ((cashPrice - milesPlusCashCash) / milesPlusCashMiles) * 100.0 : nil

    var advice: String? = nil
    if bestOption == "Miles" && cpmMiles > 1.5 {
        advice = "🎯 Great redemption value! Above average cents-per-mile."
    } else if bestOption == "Miles + Cash", let cpmMixed, cpmMixed > 1.5 {
        advice = "🎯 Good value for your miles in the Miles + Cash option!"
    }

    return PurchaseComparisonResult(
        milesCashValueLow: milesValue.low,
        milesCashValueHigh: milesValue.high,
        totalCostMilesLow: totalCostMilesLow,
        totalCostMilesHigh: totalCostMilesHigh,
        totalCostMixedLow: totalCostMixedLow,
        totalCostMixedHigh: totalCostMixedHigh,
        totalCostCash: cashPrice,
        cpmMiles: cpmMiles,
        cpmMixed: cpmMixed,
        bestOption: bestOption,
        verdict: "✅ Best Option: \(bestOption)",
        advice: advice
    )
}

// MARK: - Buy Miles Offer

struct BuyMilesResult {
    let milesCashValueLow: Double
    let milesCashValueHigh: Double
    let totalCostMilesLow: Double
    let totalCostMilesHigh: Double
    let totalCostCash: Double
    let cpmMiles: Double
    let advice: String?
}

func evaluateMilesPurchase(milesPrice: Double, cashPrice: Double) -> BuyMilesResult {
    let value = calculateMilesValue(miles: milesPrice)
    let cpmMiles = milesPrice > 0 ? (cashPrice / milesPrice) * 100.0 : 0
    var advice: String? = nil
    if cpmMiles < 1.2 {
        advice = "🎯 Great redemption value! Above average cents-per-mile."
    }
    return BuyMilesResult(
        milesCashValueLow: value.low,
        milesCashValueHigh: value.high,
        totalCostMilesLow: value.low,
        totalCostMilesHigh: value.high,
        totalCostCash: cashPrice,
        cpmMiles: cpmMiles,
        advice: advice
    )
}

// MARK: - Relative Upgrade vs Base Fare

func evaluateRelativeUpgradeCost(baseFare: Double, upgradeCost: Double) -> String? {
    guard baseFare > 0 else { return nil }
    if upgradeCost < 0.5 * baseFare {
        return "✅ Upgrade is reasonably priced relative to your original fare."
    } else if upgradeCost < 0.8 * baseFare {
        return "🟡 Upgrade is borderline—consider only for longer flights or big comfort boost."
    } else {
        return "❌ Upgrade is expensive compared to your base fare."
    }
}


