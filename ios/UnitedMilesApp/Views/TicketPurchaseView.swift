import SwiftUI

struct TicketPurchaseView: View {
    @State private var milesPrice: Double = 0
    @State private var milesPlusCashMiles: Double = 0
    @State private var cashPrice: Double = 0
    @State private var milesPlusCashCash: Double = 0

    @State private var result: PurchaseComparisonResult? = nil

    var body: some View {
        NavigationStack {
            Form {
                Section("Miles Redemption") {
                    Stepper(value: $milesPrice, in: 0...1_000_000, step: 1000) {
                        HStack { Text("Miles Required"); Spacer(); Text("\(Int(milesPrice))") }
                    }
                }

                Section("Miles + Cash") {
                    Stepper(value: $milesPlusCashMiles, in: 0...1_000_000, step: 1000) {
                        HStack { Text("Miles"); Spacer(); Text("\(Int(milesPlusCashMiles))") }
                    }
                    HStack {
                        Text("Cash ($)")
                        Spacer()
                        TextField("0", value: $milesPlusCashCash, format: .number)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                    }
                }

                Section("Full Cash Ticket") {
                    HStack {
                        Text("Price ($)")
                        Spacer()
                        TextField("0", value: $cashPrice, format: .number)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                    }
                }

                Button("Evaluate Best Purchase Option") {
                    result = evaluateBestOption(
                        milesPrice: milesPrice,
                        cashPrice: cashPrice,
                        milesPlusCashMiles: milesPlusCashMiles,
                        milesPlusCashCash: milesPlusCashCash
                    )
                }

                if let result {
                    Section("Ticket Purchase Analysis") {
                        LabeledContent("Miles Value") {
                            Text("\(formatCurrency(result.milesCashValueLow)) - \(formatCurrency(result.milesCashValueHigh))")
                        }
                        LabeledContent("Total Cost (Miles Only)") {
                            Text("\(formatCurrency(result.totalCostMilesLow)) - \(formatCurrency(result.totalCostMilesHigh))")
                        }
                        if let low = result.totalCostMixedLow, let high = result.totalCostMixedHigh {
                            LabeledContent("Total Cost (Miles + Cash)") {
                                Text("\(formatCurrency(low)) - \(formatCurrency(high))")
                            }
                        }
                        LabeledContent("Total Cost (Cash)") { Text("\(formatCurrency(result.totalCostCash))") }
                    }

                    Section("Value Assessment") {
                        Text(result.verdict)
                        if result.cpmMiles > 0 {
                            LabeledContent("CPM (Miles Only)") { Text("\(String(format: "%.2f", result.cpmMiles)) cents") }
                        }
                        if let cpmMixed = result.cpmMixed {
                            LabeledContent("CPM (Miles + Cash)") { Text("\(String(format: "%.2f", cpmMixed)) cents") }
                        }
                        if let advice = result.advice { Text(advice) }
                    }
                }
            }
            .navigationTitle("Ticket Purchase")
        }
    }
}

struct TicketPurchaseView_Previews: PreviewProvider {
    static var previews: some View {
        TicketPurchaseView()
    }
}


