import SwiftUI

struct AwardAcceleratorView: View {
    @State private var miles: Double = 0
    @State private var pqp: Double = 0
    @State private var cost: Double = 0

    @State private var result: AcceleratorResult? = nil

    var body: some View {
        NavigationStack {
            Form {
                Section("Inputs") {
                    Stepper(value: $miles, in: 0...1_000_000, step: 1000) {
                        HStack { Text("Miles Offered"); Spacer(); Text("\(Int(miles))") }
                    }
                    Stepper(value: $pqp, in: 0...10_000, step: 100) {
                        HStack { Text("PQP Offered"); Spacer(); Text("\(Int(pqp))") }
                    }
                    HStack {
                        Text("Total Cost ($)")
                        Spacer()
                        TextField("0", value: $cost, format: .number)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                    }
                }

                Button("Evaluate Award Accelerator") {
                    result = evaluateAccelerator(miles: miles, pqp: pqp, cost: cost)
                }

                if let result {
                    Section("Award Accelerator Analysis") {
                        LabeledContent("Miles Worth") { Text("\(formatCurrency(result.milesWorthLow)) - \(formatCurrency(result.milesWorthHigh))") }
                        if miles > 0 { LabeledContent("Cost Per Mile") { Text("\(String(format: "%.3f", result.costPerMile)) cents") } }
                        if let pqpLow = result.pqpCostLow { LabeledContent("PQP Cost") { Text("\(formatCurrency(pqpLow))/PQP") } }
                    }
                    Section("Value Assessment") {
                        Text(result.verdict)
                        if miles > 0 && cost > 0 {
                            let cpm = result.cpm
                            if cpm < 1.0 {
                                Text("You're paying only \(String(format: "%.3f", cpm)) cents per mile. Below the typical valuation of 1.2–1.5¢.")
                                    .foregroundStyle(.green)
                            } else if cpm < 1.2 {
                                Text("You're paying \(String(format: "%.3f", cpm)) cents per mile. Slightly below 1.2–1.5¢ typical range.")
                                    .foregroundStyle(.secondary)
                            } else {
                                Text("You're paying \(String(format: "%.3f", cpm)) cents per mile. Above the typical 1.2–1.5¢ range.")
                                    .foregroundStyle(.orange)
                            }
                        }
                        if pqp > 0 && cost > 0 {
                            let ratio = pqp / cost
                            if ratio > 0.65 {
                                Text("Excellent PQP earning rate (\(String(format: "%.2f", ratio)) PQP per dollar).")
                                    .foregroundStyle(.green)
                            } else if ratio > 0.5 {
                                Text("Decent PQP earning rate (\(String(format: "%.2f", ratio)) PQP per dollar).")
                                    .foregroundStyle(.secondary)
                            } else {
                                Text("Below-average PQP earning rate (\(String(format: "%.2f", ratio)) PQP per dollar).")
                                    .foregroundStyle(.orange)
                            }
                        } else if miles > 0 && cost > 0 {
                            Text("This offer doesn't include PQP, so it only helps with award travel, not elite status progress.")
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
            .navigationTitle("Award Accelerator")
        }
    }
}

struct AwardAcceleratorView_Previews: PreviewProvider {
    static var previews: some View {
        AwardAcceleratorView()
    }
}


