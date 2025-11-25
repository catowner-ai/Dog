package J1120;

import java.util.Scanner;

public class J1120_04 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		Scanner scn = new Scanner(System.in);
		String str1,str2;
		System.out.print("請輸入第一個字串:");
		str1 = scn.nextLine();
		System.out.print("請輸入第二個字串:");
		str2 = scn.nextLine(); 
		System.out.print("您所輸入的字串如下:\n"+str1+"\n"+str2);
		scn.close();
	}

}
