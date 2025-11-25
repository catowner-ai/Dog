package J1121_1;

import java.util.Scanner;

public class J1121_6 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		Scanner scn = new Scanner(System.in);
		int x;
		String str1 = new String("您輸入的是正數或0");
		    	       
		System.out.print("請輸入一個整數:");        
		x = Integer.parseInt(scn.nextLine());
		if(x<0)  
		        str1 = "您輸入的是負數";
		System.out.println(str1);
		
	}

}
