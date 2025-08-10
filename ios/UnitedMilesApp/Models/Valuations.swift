import Foundation

enum Valuations {
    static let mileValueLow: Double = 0.012
    static let mileValueHigh: Double = 0.015
    static let upgradeComfortHours: Int = 6
}

enum CabinClass: String, CaseIterable, Identifiable {
    case economy = "Economy"
    case premiumPlus = "Premium Plus"
    case business = "Business (Polaris)"

    var id: String { rawValue }
}

struct UpgradeMultipliers {
    static func multiplier(from: CabinClass, to: CabinClass) -> Double {
        switch (from, to) {
        case (.economy, .premiumPlus): return 1.2
        case (.economy, .business): return 1.5
        case (.premiumPlus, .business): return 1.3
        default: return 1.0
        }
    }
}


