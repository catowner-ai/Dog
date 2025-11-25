/*習題一：
-----------------------------------------------------------
設計一Java程式，輸入姓名後印出：Hi！姓名
另輸入兩個整數，中間用空白間隔，印出兩個整數相除的結果。

●執行範例如下：
請輸入姓名：Simon
Hi! Simon !
請輸入兩個整數，中間用空白間隔：17 3
17 除以 3 商為 5 餘數 2
*/
package J1120;

import java.util.Scanner;

public class J1120_ex {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // 輸入姓名
        System.out.print("請輸入姓名：");
        String name = scanner.nextLine();  // 讀取整行，支援中英文姓名

        System.out.println("Hi! " + name + " !");

        // 輸入兩個整數
        System.out.print("請輸入兩個整數，中間用空白間隔：");
        int a = scanner.nextInt();
        int b = scanner.nextInt();

        int quotient = a / b;   // 商
        int remainder = a % b;  // 餘數

        // 輸出除法結果
        System.out.println(a + " 除以 " + b + " 商為 " + quotient + " 餘數 " + remainder);

        scanner.close();
    }
}