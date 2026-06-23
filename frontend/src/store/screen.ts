import { create } from "zustand";

interface ScreenState {
  /** IDs of products the user is currently viewing on screen. */
  productsOnScreen: number[];
  setProductsOnScreen: (ids: number[]) => void;
}

export const useScreenStore = create<ScreenState>((set) => ({
  productsOnScreen: [],
  setProductsOnScreen: (ids) => set({ productsOnScreen: ids }),
}));
