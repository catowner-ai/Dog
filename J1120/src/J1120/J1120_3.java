package J1120;

import java.util.Scanner;

public class J1120_3 {

    public static void main(String[] args) {
        int k;
        double Ans;
        Scanner scn = new Scanner(System.in);
        
        System.out.print("計算3.5的k次方?\n請輸入k=");
        k = scn.nextInt();                 // 直接用 nextInt() 比較簡單
        
        Ans = power(3.5, k);               // 呼叫下面的 power 方法
        
        System.out.println("3.5的" + k + "次方=" + Ans);
        
        scn.close();
    }
    
    // 這個方法必須寫在 main 外面，且跟 main 同一個 class 裡面
    public static double power(double X, int n) {
        double powerXn = 1.0;
        for(int i = 1; i <= n; i++) {
            powerXn *= X;
        }
        return powerXn;
    }
}