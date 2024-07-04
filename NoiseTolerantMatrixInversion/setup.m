clear;close all;clc;
tau = 0.01;alpha = 0.1;
A = @(t) [sin(t),cos(t);-cos(t),sin(t)];
dA = @(t) [cos(t),-sin(t);sin(t),cos(t)];

% X0 = 2*A(0)'/(trace(A(0)*A(0)'));
X0 = eye(2);

output = sim('VPNTZNN.slx', 'StopTime', '10', 'Solver', 'ode4', 'FixedStep', num2str(tau));

figure;hold on;grid minor;
xlabel('tiempo(s)', 'Interpreter', 'latex');
title('$\| A(t)X(t) - I \|_F$', 'Interpreter', 'latex');
plot(output.frobNorm.Time, output.frobNorm.Data);


figure('OuterPosition',[360,90,1200,900]);
for i=1:4
    subplot(2,2,i);hold on; grid minor;
    titleHandle = title(sprintf('$x_{%d,%d}$',ceil(i/2),2-mod(i,2)), 'Interpreter', 'latex');
    set(titleHandle, 'Units', 'normalized', 'Position', [0.5, 0.85, 0]);
    ylim([-2,2]);
    h1=plot(output.invNoiseA.Time, output.invNoiseA.Data(:,i), 'Color', '#C5D86D');
    h2=plot(output.invA.Time, output.invA.Data(:,i), 'r', 'LineWidth',2);
    h3=plot(output.X.Time, output.X.Data(:,i), 'b', 'LineWidth',2);
end

legend_labels = {'$(A(t)+D(t))^{-1}$', '$A^{-1}(t)$', '$X(t)$'};
hL = legend([h1, h2, h3], legend_labels, 'Interpreter', 'latex');
newPosition = [0.5 0.5 0.01 0.01];
newUnits = 'normalized';
set(hL, 'Position', newPosition, 'Units', newUnits);
% legend boxoff % remove box around legend

figure('OuterPosition',[360,90,1200,900]);
for i=1:4
    subplot(2,2,i);hold on; grid minor;
    titleHandle = title(sprintf('$A_{%d,%d}$',ceil(i/2),2-mod(i,2)), 'Interpreter', 'latex');
    set(titleHandle, 'Units', 'normalized', 'Position', [0.5, 0.85, 0]);
    ylim([-2,2]);
    h1=plot(output.noiseA.Time, output.noiseA.Data(:,i), 'r');
    h2=plot(output.A.Time, output.A.Data(:,i), 'b', 'LineWidth',2);
end
legend_labels = {'$A(t) + D(t)$', '$A(t)$'};
hL = legend([h1, h2], legend_labels, 'Interpreter', 'latex');
newPosition = [0.5 0.5 0.01 0.01];
newUnits = 'normalized';
set(hL, 'Position', newPosition, 'Units', newUnits);
legend boxoff % remove box around legend

figure;hold on; grid minor;
xlabel('tiempo(s)', 'Interpreter', 'latex');
title('Ruido agregado $D(t)$', 'Interpreter', 'latex');
plot(output.noise.Time, output.noise.Data);