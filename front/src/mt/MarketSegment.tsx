import { ButtonGroup, Button } from "@material-tailwind/react";

export type Market = "korean" | "global";

export default function MarketSegment({
  value,
  onChange,
}: {
  value: Market;
  onChange: (v: Market) => void;
}) {
  return (
    <div className="p-3 bg-white text-gray-900">
      <ButtonGroup size="sm" variant="text" className="rounded-md">
        <Button
          onClick={() => onChange("korean")}
          aria-pressed={value === "korean"}
          className={
            value === "korean"
              ? "!bg-black !text-white"
              : "!bg-gray-200 !text-gray-600 hover:!bg-gray-300"
          }
          type="button"
        >
          국내
        </Button>

        <Button
          onClick={() => onChange("global")}
          aria-pressed={value === "global"}
          className={
            value === "global"
              ? "!bg-black !text-white"
              : "!bg-gray-200 !text-gray-600 hover:!bg-gray-300"
          }
          type="button"
        >
          해외
        </Button>
      </ButtonGroup>
    </div>
  );
}
