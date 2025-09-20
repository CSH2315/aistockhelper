import React, { type ErrorInfo } from "react";

type Props = { children: React.ReactNode };
type State = { error: Error | null };

export default class ErrorBoundary extends React.Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Material chunk error:", error, info);
  }

  render() {
    const { error } = this.state;
    if (error) {
      const text = `${error.name}: ${error.message}`;
      return (
        <pre
          style={{
            whiteSpace: "pre-wrap",
            padding: 16,
            background: "#fff0f0",
            color: "#900",
            border: "1px solid #f99",
            borderRadius: 8,
          }}
        >
          ⚠️ Material 컴포넌트 로드 중 오류:{"\n\n"}
          {text}
        </pre>
      );
    }
    return this.props.children;
  }
}
