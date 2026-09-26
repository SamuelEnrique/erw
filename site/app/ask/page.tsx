import type { Metadata } from "next";
import { AskForm } from "./AskForm";

export const metadata: Metadata = { title: "Ask" };

export default function AskPage() {
  return (
    <>
      <h1 className="mb-1 text-3xl">Ask the warehouse</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        A question about US energy prices, demand, generation, projects or news, answered only from the ERW tables this site reads. Every number in an
        answer comes from a query of a table, and the answer names the table and its source report; a number that cannot be traced to a query is not
        shown. If the warehouse does not hold the answer, it says so. Public tables only; power prices and demand cover the last 90 days. At most 10
        questions per hour.
      </p>
      <AskForm />
    </>
  );
}
