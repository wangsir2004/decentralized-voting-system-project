import type { Eip1193Provider } from "ethers";

declare global {
  // MetaMask 注入的 provider 不属于浏览器标准类型，这里为 window.ethereum 补充声明。
  interface Window {
    ethereum?: Eip1193Provider & {
      isMetaMask?: boolean;
      on?: (event: string, handler: (...args: unknown[]) => void) => void;
      removeListener?: (event: string, handler: (...args: unknown[]) => void) => void;
    };
  }
}

export {};
