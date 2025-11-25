package J1124;

import java.util.Scanner;

public class J1124_5 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		Scanner scn = new Scanner(System.in);
		int num, n, sum;
		do {
		    System.out.print("請輸入1~15正整數來計算階乘值: ");
		    num = scn.nextInt();
		} while (num < 1 || num > 15);
		n = num;
		sum = 1;
		do {
		    sum *= n--;
		} while (n > 0);
		System.out.printf("%d! = %d %n", num, sum);
		scn.close();
	}

}
