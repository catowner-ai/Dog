package J1124;

import java.util.Scanner;

public class J1124_9 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		int t;
		Scanner scn = new Scanner(System.in);
		System.out.print("請輸入要印出的三角形高度：");
		t = scn.nextInt();
		for(int i=0;i<t;i++) {
		    for(int j=0;j<i+1;j++) {
		        System.out.print("*");
		    }
		    System.out.println();
		scn.close();
	}
	}
}
