import SwiftUI

struct UpgradeOfferView: View {
    @State private var fromClass: CabinClass = .economy
    @State private var toClass: CabinClass = .business
    @State private var miles: Double = 0
    @State private var cashCost: Double = 0
    @State private var fullCashUpgrade: Double = 0
    @State private var fullFareCost: Double = 0
    @State private var baseFare: Double = 0
    @State private var baseFareMiles: Double = 0
    @State private var travelHours: Int = 5

    @State private var result: UpgradeResult? = nil

    var body: some View {
        NavigationStack {
            Form {
                Section("Cabin Classes") {
                    Picker("From", selection: $fromClass) {
                        ForEach(CabinClass.allCases) { cls in Text(cls.rawValue).tag(cls) }
                    }
                    Picker("To", selection: $toClass) {
                        ForEach(CabinClass.allCases) { cls in Text(cls.rawValue).tag(cls) }
                    }
                }

                Section("Upgrade Inputs") {
                    Stepper(value: $miles, in: 0...1_000_000, step: 1000) {
                        HStack { Text("Miles (Miles + Cash)"); Spacer(); Text("\(Int(miles))") }
                    }
                    currencyField(title: "Cash for Miles + Cash ($)", value: $cashCost)
                    currencyField(title: "Cash-Only Upgrade ($)", value: $fullCashUpgrade)
                    currencyField(title: "Full-Fare Business/First ($)", value: $fullFareCost)
                    currencyField(title: "Base Fare Paid ($)", value: $baseFare)
                    Stepper(value: $baseFareMiles, in: 0...1_000_000, step: 1000) {
                        HStack { Text("Base Fare Miles"); Spacer(); Text("\(Int(baseFareMiles))") }
                    }
                    Stepper(value: $travelHours, in: 1...20, step: 1) {
                        HStack { Text("Flight Duration (hours)"); Spacer(); Text("\(travelHours)h") }
                    }
                }

                Button("Evaluate Upgrade Offer") {
                    var adjustedBaseFare = baseFare
                    if baseFareMiles > 0 {
                        let milesValue = calculateMilesValue(miles: baseFareMiles)
                        adjustedBaseFare += milesValue.high
                    }
                    result = evaluateUpgrade(
                        miles: miles,
                        cashCost: cashCost,
                        fullCashUpgrade: fullCashUpgrade,
                        fullFareCost: fullFareCost,
                        travelHours: travelHours,
                        fromClass: fromClass,
                        toClass: toClass
                    )
                    // attach base fare verdict by overlaying in UI below
                }

                if let result {
                    Section("Upgrade Analysis") {
                        LabeledContent("Miles Worth") {
                            Text("\(formatCurrency(result.milesWorthLow)) - \(formatCurrency(result.milesWorthHigh))")
                        }
                        if let low = result.totalMilesCashUpgradeLow, let high = result.totalMilesCashUpgradeHigh {
                            LabeledContent("Miles + Cash Upgrade Cost") { Text("\(formatCurrency(low)) - \(formatCurrency(high))") }
                        } else {
                            LabeledContent("Miles + Cash Upgrade Cost") { Text("N/A") }
                        }
                        LabeledContent("Cash-Only Upgrade Cost") { Text("\(formatCurrency(result.totalCashUpgrade))") }
                        LabeledContent("Full-Fare Business/First") { Text("\(formatCurrency(result.fullFarePrice))") }
                    }

                    Section("Final Verdict") {
                        Text(result.verdict)
                        if let warning = result.warning { Text(warning).foregroundStyle(.red) }
                        if travelHours >= Valuations.upgradeComfortHours {
                            Text("Long flight (\(travelHours)h) increases upgrade value by \(Int((result.comfortFactor - 1) * 100))%.")
                                .foregroundStyle(.secondary)
                        }
                        if let relativeMsg = evaluateRelativeUpgradeCost(baseFare: (baseFare + calculateMilesValue(miles: baseFareMiles).high), upgradeCost: fullCashUpgrade) {
                            Text(relativeMsg)
                        }
                    }
                }
            }
            .navigationTitle("Upgrade Offer")
        }
    }

    @ViewBuilder
    private func currencyField(title: String, value: Binding<Double>) -> some View {
        HStack {
            Text(title)
            Spacer()
            TextField("0", value: value, format: .number)
                .keyboardType(.decimalPad)
                .multilineTextAlignment(.trailing)
        }
    }
}

struct UpgradeOfferView_Previews: PreviewProvider {
    static var previews: some View {
        UpgradeOfferView()
    }
}


