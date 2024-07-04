% Code only to create the visualization of the problem
close all; clear; clc;
t = rand*20;
F = @(X1, X2)(sin(t)/4 + 1)*X1.^2 + (cos(t)/4 + 1)*X2.^2 + cos(t)*X1.*X2 + sin(3*t)*X1 + cos(3*t)*X2;
x1 = linspace(-2*pi,2*pi,20);
x1_full = linspace(-2*pi,2*pi,200);
x2 = linspace(-2*pi,2*pi,20);
z_range = linspace(0, 100, 50);
[X1_, Z] = meshgrid(x1, z_range);
[X1,X2] = meshgrid(x1,x2);


f = F(X1, X2);
cnt_x2 = (cos(2*t) - sin(4*t)*X1_) ./ cos(4*t);
inter_x2 = (cos(2*t) - sin(4*t)*x1_full) ./ cos(4*t);
s = surf(X1, X2, f,'FaceAlpha',0.5,'EdgeColor','none');hold on;view([-109,18]);
surf(X1_, cnt_x2, Z,'FaceAlpha',0.5,'EdgeColor','none','FaceColor',[0.5,0,0]);
plot3(x1_full, inter_x2, F(x1_full, inter_x2), 'Color', [0,0,0], 'LineWidth', 2);
title(strcat("Tiempo: ", num2str(t)));
xlim([-2*pi,2*pi]);ylim([-2*pi,2*pi]);zlim([-1,100]);
fig = gcf;
fig.Position = [560,140,1200,800];
filename = strcat('qp_time_', num2str(t*100),'.eps');
print('-depsc', filename);