import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Upload, FileText, BarChart3, PieChart, FileDown } from "lucide-react";
import { ResponsiveContainer, Pie, PieChart as RechartsPieChart, Cell, BarChart as RechartsBarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";

const COLORS = ["#4B8BBE", "#306998", "#FFE873", "#FFD43B", "#646464"];

export default function Dashboard() {
  const [fileName, setFileName] = useState("");
  const [summary, setSummary] = useState("");
  const [uploaded, setUploaded] = useState(false);
  const [totalValue, setTotalValue] = useState("$1.2M");

  const allocation = [
    { name: "Equities", value: 68 },
    { name: "Fixed Income", value: 22 },
    { name: "Alternatives", value: 10 },
  ];

  const topHoldings = [
    { name: "AAPL", value: 320000 },
    { name: "MSFT", value: 240000 },
    { name: "VTI", value: 180000 },
    { name: "GOOGL", value: 150000 },
    { name: "TSLA", value: 120000 },
  ];

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      setUploaded(true);

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch("https://api.openai.com/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${process.env.NEXT_PUBLIC_OPENAI_API_KEY}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "gpt-4",
            messages: [
              { role: "system", content: "You are a financial analyst assistant helping summarize brokerage portfolios." },
              { role: "user", content: `Parse and summarize this portfolio statement: ${file.name}. Provide insights on allocation, concentration risk, and rebalancing opportunities.` }
            ]
          })
        });

        const result = await response.json();
        const aiSummary = result.choices?.[0]?.message?.content || "Unable to generate summary.";
        setSummary(aiSummary);
      } catch (error) {
        console.error("AI summary error:", error);
        setSummary("Error generating summary.");
      }
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <h1 className="text-4xl font-bold tracking-tight">📊 AI-Powered Investment Dashboard</h1>

      <Card className="shadow-lg">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <Upload className="w-5 h-5 text-gray-600" />
            <Input type="file" onChange={handleUpload} className="w-full" />
          </div>
          {uploaded && (
            <p className="mt-4 text-sm text-gray-600">Uploaded: {fileName}</p>
          )}
        </CardContent>
      </Card>

      {uploaded && (
        <>
          <Card className="shadow">
            <CardContent className="p-6">
              <div className="flex items-center mb-3">
                <FileText className="w-5 h-5 text-gray-600 mr-2" />
                <h2 className="text-2xl font-semibold">AI Portfolio Summary</h2>
              </div>
              <p className="text-gray-700 text-lg leading-relaxed whitespace-pre-line">{summary}</p>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <Card className="shadow">
              <CardContent className="p-6">
                <div className="flex items-center mb-3">
                  <PieChart className="w-5 h-5 text-gray-600 mr-2" />
                  <h2 className="text-xl font-semibold">Allocation Breakdown</h2>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <RechartsPieChart>
                    <Pie data={allocation} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                      {allocation.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="shadow">
              <CardContent className="p-6">
                <div className="flex items-center mb-3">
                  <BarChart3 className="w-5 h-5 text-gray-600 mr-2" />
                  <h2 className="text-xl font-semibold">Top Holdings</h2>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <RechartsBarChart data={topHoldings} layout="vertical">
                    <XAxis type="number" tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                    <YAxis type="category" dataKey="name" width={70} />
                    <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                    <Bar dataKey="value" fill="#4B8BBE" />
                  </RechartsBarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-end">
            <Button className="mt-6" variant="outline">
              <FileDown className="w-4 h-4 mr-2" /> Download PDF Report
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
