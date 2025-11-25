package J1124;

import java.util.Scanner;

public class J1124_10 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		Scanner scn = new Scanner(System.in);
		int num = 0;
		String sel;
		do { 
		    System.out.println("********** 選單  **********");
		    System.out.println("\tA. 平方");
		    System.out.println("\tB. 三次方");
		    System.out.println("\tC. 離開系統");
		    System.out.println("*************************");
		    do { // 直到輸入A~C才離開迴圈
		        System.out.print("請選擇功能: ");
		        sel = scn.next().toUpperCase(); // 輸入字母轉成大寫 toLowerCase轉小寫
		    } while ("ABC".indexOf(sel) == -1);
		    if (!(sel.equals("C"))) {
		        System.out.print("請輸入整數: ");
		        num = scn.nextInt();
		    }
		    switch (sel) {
		    case "A":
		        System.out.printf(" %d 的平方 = %d%n", num, num * num);
		        break;
		    case "B":
		        System.out.printf(" %d 的三次方 = %d%n", num, num * num * num);
		        break;
		    case "C":
		        System.out.println("結束程式");
		    }
		} while (!(sel.equals("C")));// 只要輸入的不是大小寫的C，就繼續執行程式
		scn.close();
	}

}
