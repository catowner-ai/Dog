package J1124;

import java.util.Scanner;

public class J1124_2 {

    public static void main(String[] args) {
        Scanner scn = new Scanner(System.in);
        int price = 0;
        int total = 0;

        while (true) {
            System.out.print("請輸入單價 (輸入 -1 結束): ");
            price = scn.nextInt();

            if (price == -1) {
                break;  // 輸入 -1 就結束輸入
            }

            if (price > 0) {
                total += price;
            } else if (price < 0) {
                System.out.println("單價不可為負數，已忽略此筆資料");
            }
        }

        System.out.printf("總價 = %d 元%n", total);
        scn.close();
    }
}