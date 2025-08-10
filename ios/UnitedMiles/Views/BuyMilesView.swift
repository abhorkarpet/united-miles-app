import SwiftUI

struct BuyMilesView: View {
    @State private var cashPrice: Double = 0
    @State private var milesPrice: Double = 0
    @State private var bonusMiles: Double = 0

    @State private var result: BuyMilesResult? = nil

    var body: some View {
        NavigationStack {
            Form {
                Section("Inputs") {
                    HStack {
                        Text("Purchase Price ($)")
                        Spacer()
                        TextField("0", value: $cashPrice, format: .number)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                    }
                    Stepper(value: $milesPrice, in: 0...1_000_000, step: 1000) {
                        HStack { Text("Miles"); Spacer(); Text("\(Int(milesPrice))") }
                    }
                    Stepper(value: $bonusMiles, in: 0...1_000_000, step: 1000) {
                        HStack { Text("Bonus Miles"); Spacer(); Text("\(Int(bonusMiles))") }
                    }
                }

                Button("Evaluate the Offer") {
                    let totalMiles = milesPrice + bonusMiles
                    result = evaluateMilesPurchase(milesPrice: totalMiles, cashPrice: cashPrice)
                }

                if let result {
                    Section("Miles Purchase Analysis") {
                        LabeledContent("Miles Value") {
                            Text("\(formatCurrency(result.milesCashValueLow)) - \(formatCurrency(result.milesCashValueHigh))")
                        }
                        LabeledContent("Total Cost (Cash)") { Text("\(formatCurrency(result.totalCostCash))") }
                    }
                    Section("Value Assessment") {
                        LabeledContent("CPM (Miles Only)") { Text("\(String(format: "%.2f", result.cpmMiles)) cents per mile") }
                        if let advice = result.advice { Text(advice) }
                        if result.cpmMiles < 1.0 {
                            Text("Excellent value: \(String(format: "%.2f", result.cpmMiles)) cpm (avg: 1.2–1.5¢)")
                                .foregroundStyle(.green)
                        } else if result.cpmMiles < 1.5 {
                            Text("Good value: \(String(format: "%.2f", result.cpmMiles)) cpm (below typical 1.2–1.5¢)")
                                .foregroundStyle(.secondary)
                        } else {
                            Text("Below average value: \(String(format: "%.2f", result.cpmMiles)) cpm (above typical 1.2–1.5¢)")
                                .foregroundStyle(.orange)
                        }
                    }
                }
            }
            .navigationTitle("Buy Miles")
        }
    }
}

struct BuyMilesView_Previews: PreviewProvider {
    static var previews: some View {
        BuyMilesView()
    }
}


